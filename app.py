import streamlit as st
from typing import List
from openai import OpenAI
from pydantic import BaseModel, Field

# ==========================================
# 網頁配置與視覺主題（盲盒風格）
# ==========================================
st.set_page_config(page_title="🎁 AI 旅遊盲盒行程生成器", page_icon="🎁", layout="wide")
st.title("🎁 專案項目：AI 智能旅遊盲盒行程生成器")
st.markdown("---")

# 側邊欄金鑰設定
st.sidebar.header("🔑 後端金鑰設定")
api_key = st.sidebar.text_input("輸入 OpenAI API Key", type="password")

# ==========================================
# 資料結構定義 (對應步驟 3 的結構化呈現)
# ==========================================
class ActivityDetail(BaseModel):
    time_slot: str = Field(description="時間段，例如：09:00 - 11:00")
    location: str = Field(description="盲盒推薦的景點或餐廳名稱")
    activity_description: str = Field(description="詳細行程細節、必吃必玩理由、交通指南")
    estimated_cost: int = Field(description="該活動的預估花費")

class DailyItinerary(BaseModel):
    day_number: int = Field(description="第幾天")
    date_note: str = Field(description="當日盲盒主題，例如：熱血動漫日、微醺微胖夜")
    activities: List[ActivityDetail] = Field(description="當天的行程列表")
    daily_cost_subtotal: int = Field(description="當日花費小計")

class BlindBoxItinerary(BaseModel):
    destination: str = Field(description="旅遊目的地")
    total_days: int = Field(description="總天數")
    currency: str = Field(description="貨幣單位")
    total_estimated_budget: int = Field(description="整趟盲盒行程總花費")
    blind_box_intro: str = Field(description="揭曉盲盒！對這趟神秘行程的風格總結與驚喜點評")
    daily_schedule: List[DailyItinerary] = Field(description="每日行程明細")

# ==========================================
# 圖片步驟 1：接收使用者的輸入
# ==========================================
col1, col2 = st.columns(2)
with col1:
    city = st.text_input("📍 你想去哪個城市玩？（例如：東京、首爾、曼谷）", value="東京")
    days = st.number_input("📅 預計去幾天？", min_value=1, max_value=7, value=3)
with col2:
    budget = st.text_input("💰 預算大約是多少元？（含當地吃喝玩樂）", value="30000元新台幣")
    style = st.selectbox(
        "🎯 想要的旅遊風格是？",
        ["特種兵極限充實流", "慵懶隨性貴婦流", "宅男動漫聖地巡禮", "吃貨必嚐在地美食", "純盲盒隨機驚喜！"]
    )

# ==========================================
# 圖片步驟 2 & 3：點擊按鈕，傳送需求給 AI 並顯示在網頁上
# ==========================================
if st.button("🎲 開啟我的 AI 旅遊盲盒！"):
    if not api_key:
        st.error("❌ 請記得在左側輸入 API 金鑰，才能啟動 AI 核心邏輯喔！")
    else:
        # 1. 轉化為與你圖片高度一致的 Prompt 邏輯
        prompt = f"我想去 {city} 玩 {days} 天，預算大約 {budget} 元，偏好 {style} 風格。"
        
        with st.spinner("🧙‍♂️ AI 正在瘋狂計算與調配你的盲盒行程..."):
            try:
                # 2. 呼叫大模型 API（這裡使用支援結構化輸出的 gpt-4o 模型）
                client = OpenAI(api_key=api_key)
                response = client.beta.chat.completions.parse(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system", 
                            "content": "你是一個充滿驚喜的旅遊盲盒規劃專家。請為使用者打造一份精準、充滿儀式感、且時間金額分配合理的行程。"
                        },
                        {"role": "user", "content": prompt}
                    ],
                    response_format=BlindBoxItinerary,
                    temperature=0.85 # 稍微提高創造力，更符合盲盒的驚喜感
                )
                
                # 3. 把 AI 給你的建議解析出來
                result: BlindBoxItinerary = response.choices[0].message.parsed
                
                # ---- 網頁前端渲染（對應圖片的 return response.text 並美化） ----
                st.balloons() # 噴發慶祝氣球
                st.success("🎉 旅遊盲盒揭曉成功！")
                
                st.header(f"🎁 你的 {result.destination} · {result.total_days}天 盲盒行程表")
                st.markdown(f"### 💡 **盲盒主打星：** {result.blind_box_intro}")
                st.metric(label="💰 預估總花費", value=f"{result.total_estimated_budget:,.0f} {result.currency}")
                
                st.divider()
                
                # 展開每天的細節
                for day in result.daily_schedule:
                    with st.expander(f"📅 第 {day.day_number} 天：{day.date_note} (當天小計: {day.daily_cost_subtotal:,.0f} {result.currency})", expanded=True):
                        
                        # 建立精美的表格結構
                        table_data = []
                        for act in day.activities:
                            table_data.append({
                                "時間段": act.time_slot,
                                "解鎖景點/餐廳": act.location,
                                "盲盒細節與注意事項": act.activity_description,
                                "預估花費": f"{act.estimated_cost:,.0f} {result.currency}"
                            })
                        st.table(table_data)
                        
            except Exception as e:
                st.error(f"連線或解析失敗，請確認 Key 是否有餘額。錯誤原因: {e}")
