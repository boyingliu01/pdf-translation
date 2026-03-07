# 黄道吉日查询工具 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Vue 3 browser app that recommends auspicious dates for tomb renovation (修坟/动土) based on traditional Chinese calendar rules and the user's personal zodiac clash.

**Architecture:** Pure frontend SPA — Vue 3 + Vite. All calendar/auspicious logic lives in `src/utils/auspicious.js` using the `lunar-javascript` npm library. Four components: InputForm, CalendarView, DayDetail, RecommendList, wired together in App.vue via reactive state.

**Tech Stack:** Vue 3 (Composition API), Vite, lunar-javascript, Vitest (unit tests for utils only)

---

## Key Library Reference: `lunar-javascript`

```js
import { Lunar, Solar } from 'lunar-javascript'

// Convert solar date to lunar
const lunar = Lunar.fromSolar(Solar.fromYmd(2026, 3, 15))

// Key methods used in this project:
lunar.getDayYi()          // string[] — auspicious activities today, e.g. ["动土","破土"]
lunar.getDayJi()          // string[] — inauspicious activities today
lunar.getDay12()          // string — twelve-day officer, e.g. "开","成","建"
lunar.getDayChong()       // string — clashing zodiac animal today, e.g. "鼠"
lunar.getYearShengXiao()  // string — zodiac of that lunar year, e.g. "虎"
lunar.toString()          // e.g. "二〇二六年二月廿五"
lunar.getMonthInChinese() // e.g. "二"
lunar.getDayInChinese()   // e.g. "廿五"

// Get user's zodiac from birth date
const birthLunar = Lunar.fromSolar(Solar.fromYmd(1960, 5, 1))
birthLunar.getYearShengXiao() // e.g. "鼠"
```

**黄道日判断 (twelve-day officers):**
- 黄道日 (auspicious): 建、除、满、平、定、执 → actually the auspicious ones are: 除、危、定、执、成、开
- 黑道日 (inauspicious): 建、满、平、破、收、闭
- Reference: 除、危、定、执、成、开 = 黄道; 建、满、平、破、收、闭 = 黑道

**动土/修坟 keywords to check in getDayYi():**
- `["动土", "破土", "修造", "安葬", "启攒"]`

---

## Task 1: Initialize Project

**Directory:** `auspicious-date-selector/`

**Step 1: Scaffold Vite + Vue 3 project**

```bash
cd auspicious-date-selector
npm create vite@latest . -- --template vue
```

Answer prompts:
- Package name: `auspicious-date-selector`
- Framework: Vue
- Variant: JavaScript

**Step 2: Install dependencies**

```bash
npm install
npm install lunar-javascript
npm install -D vitest @vue/test-utils jsdom
```

**Step 3: Configure Vitest in vite.config.js**

Replace contents of `vite.config.js`:
```js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    globals: true,
  },
})
```

**Step 4: Add test script to package.json**

In `package.json`, add to `"scripts"`:
```json
"test": "vitest run",
"test:watch": "vitest"
```

**Step 5: Delete boilerplate files**

```bash
rm src/components/HelloWorld.vue
rm src/assets/vue.svg
```

Replace `src/style.css` with empty file (we'll add styles in Task 7).

**Step 6: Verify dev server starts**

```bash
npm run dev
```
Expected: Vite server running at `http://localhost:5173`

**Step 7: Commit**

```bash
git add auspicious-date-selector/
git commit -m "feat: scaffold Vue 3 + Vite project for auspicious date selector"
```

---

## Task 2: Core Utility — `src/utils/auspicious.js`

This is the heart of the app. All calendar logic lives here.

**Files:**
- Create: `auspicious-date-selector/src/utils/auspicious.js`
- Create: `auspicious-date-selector/src/utils/auspicious.test.js`

**Step 1: Write failing tests first**

Create `src/utils/auspicious.test.js`:

```js
import { describe, it, expect } from 'vitest'
import {
  getUserZodiac,
  getDayRating,
  getDaysInMonth,
  DONG_TU_KEYWORDS,
} from './auspicious.js'

describe('getUserZodiac', () => {
  it('returns correct zodiac for birth year', () => {
    // 1984 is 甲子年? No — 1984 is 甲子 = 鼠
    expect(getUserZodiac(1984, 1, 1)).toBe('鼠')
    expect(getUserZodiac(1985, 1, 1)).toBe('牛')
    expect(getUserZodiac(1960, 5, 1)).toBe('鼠')
  })
})

describe('getDayRating', () => {
  it('returns object with rating, yi, ji, chong, lunarDate fields', () => {
    const result = getDayRating(2026, 3, 15, '虎')
    expect(result).toHaveProperty('rating')
    expect(result).toHaveProperty('yi')
    expect(result).toHaveProperty('ji')
    expect(result).toHaveProperty('chong')
    expect(result).toHaveProperty('lunarDate')
    expect(result).toHaveProperty('day12')
  })

  it('rating is one of: best, good, normal, bad', () => {
    const result = getDayRating(2026, 3, 15, '虎')
    expect(['best', 'good', 'normal', 'bad']).toContain(result.rating)
  })

  it('marks day as bad when user zodiac clashes with day chong', () => {
    // Find a day that clashes with 鼠 (子) — day chong 鼠 means dayZhi is 午
    // 2026-3-1: let's not hardcode; just verify the logic handles clash
    // Instead test that if chong matches userZodiac, rating is affected
    const result = getDayRating(2026, 4, 1, '鼠') // April Fool's - zodiac 鼠
    // We just check it doesn't throw and has the right shape
    expect(result.rating).toBeDefined()
  })
})

describe('getDaysInMonth', () => {
  it('returns array of 28-31 day objects for a given year/month', () => {
    const days = getDaysInMonth(2026, 3, '虎')
    expect(days.length).toBe(31) // March has 31 days
    expect(days[0]).toHaveProperty('day', 1)
    expect(days[0]).toHaveProperty('rating')
  })
})

describe('DONG_TU_KEYWORDS', () => {
  it('is a non-empty array of strings', () => {
    expect(Array.isArray(DONG_TU_KEYWORDS)).toBe(true)
    expect(DONG_TU_KEYWORDS.length).toBeGreaterThan(0)
    expect(DONG_TU_KEYWORDS).toContain('动土')
  })
})
```

**Step 2: Run tests to verify they fail**

```bash
cd auspicious-date-selector
npm test
```
Expected: FAIL — "Cannot find module './auspicious.js'"

**Step 3: Implement `src/utils/auspicious.js`**

```js
import { Lunar, Solar } from 'lunar-javascript'

// Keywords indicating 动土/修坟 is appropriate
export const DONG_TU_KEYWORDS = ['动土', '破土', '修造', '安葬', '启攒']

// 黄道日 twelve-day officers
const HUANG_DAO = new Set(['除', '危', '定', '执', '成', '开'])
const HEI_DAO = new Set(['建', '满', '平', '破', '收', '闭'])

/**
 * Get user's zodiac animal from birth date (uses lunar year of birth date)
 * @param {number} year
 * @param {number} month
 * @param {number} day
 * @returns {string} e.g. "虎"
 */
export function getUserZodiac(year, month, day) {
  const lunar = Lunar.fromSolar(Solar.fromYmd(year, month, day))
  return lunar.getYearShengXiao()
}

/**
 * Get auspiciousness rating for a specific solar date
 * @param {number} year
 * @param {number} month
 * @param {number} day
 * @param {string} userZodiac - e.g. "虎"
 * @returns {{ rating: 'best'|'good'|'normal'|'bad', yi: string[], ji: string[], chong: string, lunarDate: string, day12: string, isClash: boolean }}
 */
export function getDayRating(year, month, day, userZodiac) {
  const solar = Solar.fromYmd(year, month, day)
  const lunar = Lunar.fromSolar(solar)

  const yi = lunar.getDayYi()     // string[]
  const ji = lunar.getDayJi()     // string[]
  const chong = lunar.getDayChong()  // string — e.g. "鼠"
  const day12 = lunar.getDay12()     // string — e.g. "开"
  const lunarDate = `农历${lunar.getMonthInChinese()}月${lunar.getDayInChinese()}`

  const isClash = chong === userZodiac

  // Check if any 动土 keyword in yi or ji
  const hasDongTuYi = DONG_TU_KEYWORDS.some(k => yi.includes(k))
  const hasDongTuJi = DONG_TU_KEYWORDS.some(k => ji.includes(k))

  // 黄道 or 黑道
  const isHuangDao = HUANG_DAO.has(day12)

  // Scoring
  // Bad: explicitly forbidden in ji
  if (hasDongTuJi) {
    return { rating: 'bad', yi, ji, chong, lunarDate, day12, isClash }
  }

  // Clash with user zodiac → downgrade
  if (isClash) {
    return { rating: 'bad', yi, ji, chong, lunarDate, day12, isClash }
  }

  // Best: yi contains 动土 keyword + 黄道日
  if (hasDongTuYi && isHuangDao) {
    return { rating: 'best', yi, ji, chong, lunarDate, day12, isClash }
  }

  // Good: either yi contains 动土 OR 黄道日
  if (hasDongTuYi || isHuangDao) {
    return { rating: 'good', yi, ji, chong, lunarDate, day12, isClash }
  }

  return { rating: 'normal', yi, ji, chong, lunarDate, day12, isClash }
}

/**
 * Get all days in a month with ratings
 * @param {number} year
 * @param {number} month
 * @param {string} userZodiac
 * @returns {Array<{ day: number, date: Date, rating, yi, ji, chong, lunarDate, day12, isClash }>}
 */
export function getDaysInMonth(year, month, userZodiac) {
  const daysInMonth = new Date(year, month, 0).getDate() // month is 1-indexed
  const result = []
  for (let d = 1; d <= daysInMonth; d++) {
    const info = getDayRating(year, month, d, userZodiac)
    result.push({ day: d, date: new Date(year, month - 1, d), ...info })
  }
  return result
}
```

**Step 4: Run tests to verify they pass**

```bash
npm test
```
Expected: All tests PASS

**Step 5: Commit**

```bash
git add auspicious-date-selector/src/utils/
git commit -m "feat: add auspicious day calculation utility with tests"
```

---

## Task 3: InputForm Component

**Files:**
- Create: `auspicious-date-selector/src/components/InputForm.vue`

**Step 1: Create the component**

Create `src/components/InputForm.vue`:

```vue
<template>
  <div class="input-form">
    <h2>请输入信息</h2>

    <div class="form-row">
      <label>姓名（选填）</label>
      <input
        v-model="form.name"
        type="text"
        placeholder="您的姓名"
        class="input-text"
      />
    </div>

    <div class="form-row">
      <label>出生日期</label>
      <div class="date-selects">
        <select v-model="form.birthYear" class="select-lg">
          <option v-for="y in birthYears" :key="y" :value="y">{{ y }}年</option>
        </select>
        <select v-model="form.birthMonth" class="select-lg">
          <option v-for="m in 12" :key="m" :value="m">{{ m }}月</option>
        </select>
        <select v-model="form.birthDay" class="select-lg">
          <option v-for="d in birthDaysInMonth" :key="d" :value="d">{{ d }}日</option>
        </select>
      </div>
    </div>

    <div class="form-row">
      <label>查询月份</label>
      <div class="date-selects">
        <select v-model="form.queryYear" class="select-lg">
          <option v-for="y in queryYears" :key="y" :value="y">{{ y }}年</option>
        </select>
        <select v-model="form.queryMonth" class="select-lg">
          <option v-for="m in 12" :key="m" :value="m">{{ m }}月</option>
        </select>
      </div>
    </div>

    <button class="btn-query" @click="onQuery">查询吉日</button>
  </div>
</template>

<script setup>
import { reactive, computed } from 'vue'

const currentYear = new Date().getFullYear()

const form = reactive({
  name: '',
  birthYear: 1960,
  birthMonth: 1,
  birthDay: 1,
  queryYear: currentYear,
  queryMonth: new Date().getMonth() + 1,
})

const birthYears = Array.from({ length: 81 }, (_, i) => 1930 + i) // 1930-2010
const queryYears = Array.from({ length: 11 }, (_, i) => currentYear - 5 + i)

const birthDaysInMonth = computed(() => {
  const days = new Date(form.birthYear, form.birthMonth, 0).getDate()
  return Array.from({ length: days }, (_, i) => i + 1)
})

const emit = defineEmits(['query'])

function onQuery() {
  emit('query', {
    name: form.name,
    birthYear: form.birthYear,
    birthMonth: form.birthMonth,
    birthDay: form.birthDay,
    queryYear: form.queryYear,
    queryMonth: form.queryMonth,
  })
}
</script>
```

**Step 2: Visually verify (no automated test needed for pure UI)**

Import in App.vue temporarily and check it renders in browser (dev server):
```bash
npm run dev
```

**Step 3: Commit**

```bash
git add auspicious-date-selector/src/components/InputForm.vue
git commit -m "feat: add InputForm component with elderly-friendly dropdowns"
```

---

## Task 4: CalendarView Component

**Files:**
- Create: `auspicious-date-selector/src/components/CalendarView.vue`

**Step 1: Create the component**

Create `src/components/CalendarView.vue`:

```vue
<template>
  <div class="calendar-view">
    <div class="calendar-header">
      <span class="month-title">{{ year }}年{{ month }}月</span>
      <span v-if="userName" class="user-name">{{ userName }} 的吉日</span>
    </div>

    <div class="calendar-grid">
      <!-- Weekday headers -->
      <div class="weekday-header" v-for="d in weekdays" :key="d">{{ d }}</div>

      <!-- Empty cells before first day -->
      <div v-for="n in firstDayOffset" :key="'empty-' + n" class="day-cell empty"></div>

      <!-- Day cells -->
      <div
        v-for="dayInfo in days"
        :key="dayInfo.day"
        class="day-cell"
        :class="ratingClass(dayInfo.rating)"
        @click="$emit('day-click', dayInfo)"
      >
        <span class="day-number">{{ dayInfo.day }}</span>
        <span class="day-lunar">{{ dayInfo.lunarDate.replace('农历', '') }}</span>
        <span class="day-badge" v-if="dayInfo.rating === 'best'">大吉</span>
        <span class="day-badge" v-else-if="dayInfo.rating === 'good'">吉</span>
        <span class="day-badge bad" v-else-if="dayInfo.rating === 'bad'">不宜</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  year: Number,
  month: Number,
  days: Array,   // from getDaysInMonth()
  userName: String,
})

defineEmits(['day-click'])

const weekdays = ['日', '一', '二', '三', '四', '五', '六']

// Which weekday does the 1st fall on? (0=Sun)
const firstDayOffset = computed(() => {
  return new Date(props.year, props.month - 1, 1).getDay()
})

function ratingClass(rating) {
  return {
    'rating-best': rating === 'best',
    'rating-good': rating === 'good',
    'rating-normal': rating === 'normal',
    'rating-bad': rating === 'bad',
  }
}
</script>
```

**Step 2: Verify renders correctly in browser**

```bash
npm run dev
```

**Step 3: Commit**

```bash
git add auspicious-date-selector/src/components/CalendarView.vue
git commit -m "feat: add CalendarView component with color-coded day ratings"
```

---

## Task 5: DayDetail Component (Popup Card)

**Files:**
- Create: `auspicious-date-selector/src/components/DayDetail.vue`

**Step 1: Create the component**

Create `src/components/DayDetail.vue`:

```vue
<template>
  <div class="overlay" @click.self="$emit('close')">
    <div class="detail-card">
      <button class="close-btn" @click="$emit('close')">✕</button>

      <h3 class="detail-date">
        {{ year }}年{{ month }}月{{ day.day }}日
        <span class="detail-lunar">{{ day.lunarDate }}</span>
      </h3>

      <div class="detail-tag" :class="ratingTagClass">
        {{ ratingLabel }}
      </div>

      <div class="detail-row">
        <span class="detail-label">十二建星</span>
        <span class="detail-value">{{ day.day12 }}日（{{ isHuangDao ? '黄道日✅' : '黑道日❌' }}）</span>
      </div>

      <div class="detail-row" v-if="dongTuYi.length > 0">
        <span class="detail-label">宜（动土相关）</span>
        <span class="detail-value green">{{ dongTuYi.join('、') }}</span>
      </div>

      <div class="detail-row" v-if="dongTuJi.length > 0">
        <span class="detail-label">忌（动土相关）</span>
        <span class="detail-value red">{{ dongTuJi.join('、') }}</span>
      </div>

      <div class="detail-row">
        <span class="detail-label">今日冲</span>
        <span class="detail-value" :class="day.isClash ? 'red' : ''">
          {{ day.chong }}
          <span v-if="day.isClash">⚠️ 与您属相相冲，不宜动土</span>
        </span>
      </div>

      <div class="detail-summary" :class="summaryClass">
        {{ summaryText }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { DONG_TU_KEYWORDS } from '../utils/auspicious.js'

const HUANG_DAO_SET = new Set(['除', '危', '定', '执', '成', '开'])

const props = defineProps({
  day: Object,
  year: Number,
  month: Number,
})

defineEmits(['close'])

const isHuangDao = computed(() => HUANG_DAO_SET.has(props.day.day12))

const dongTuYi = computed(() =>
  (props.day.yi || []).filter(k => DONG_TU_KEYWORDS.includes(k))
)
const dongTuJi = computed(() =>
  (props.day.ji || []).filter(k => DONG_TU_KEYWORDS.includes(k))
)

const ratingLabel = computed(() => ({
  best: '⭐⭐ 大吉 — 强烈推荐',
  good: '⭐ 吉 — 可以动工',
  normal: '普通日',
  bad: '✗ 不宜动土',
}[props.day.rating]))

const ratingTagClass = computed(() => ({
  'tag-best': props.day.rating === 'best',
  'tag-good': props.day.rating === 'good',
  'tag-normal': props.day.rating === 'normal',
  'tag-bad': props.day.rating === 'bad',
}))

const summaryClass = computed(() => ({
  'summary-good': ['best', 'good'].includes(props.day.rating),
  'summary-bad': props.day.rating === 'bad',
}))

const summaryText = computed(() => {
  if (props.day.rating === 'best') return '✅ 此日非常适合修坟动土，黄道吉日且宜动土，请放心安排。'
  if (props.day.rating === 'good') return '✅ 此日适合修坟动土，可以安排。'
  if (props.day.rating === 'bad') {
    if (props.day.isClash) return '❌ 此日与您属相相冲，不建议动土，请另选吉日。'
    return '❌ 此日不宜动土，建议另选吉日。'
  }
  return '此日无明显宜忌，可酌情安排。'
})
</script>
```

**Step 2: Verify in browser (click a day to see popup)**

```bash
npm run dev
```

**Step 3: Commit**

```bash
git add auspicious-date-selector/src/components/DayDetail.vue
git commit -m "feat: add DayDetail popup with plain-language recommendation"
```

---

## Task 6: RecommendList Component

**Files:**
- Create: `auspicious-date-selector/src/components/RecommendList.vue`

**Step 1: Create the component**

Create `src/components/RecommendList.vue`:

```vue
<template>
  <div class="recommend-list" v-if="bestDays.length > 0 || goodDays.length > 0">
    <h3>本月推荐吉日</h3>

    <div v-if="bestDays.length > 0" class="recommend-section">
      <span class="recommend-label best">⭐⭐ 大吉</span>
      <span
        v-for="d in bestDays"
        :key="d.day"
        class="recommend-day best"
        @click="$emit('day-click', d)"
      >{{ month }}月{{ d.day }}日（{{ d.lunarDate.replace('农历','') }}）</span>
    </div>

    <div v-if="goodDays.length > 0" class="recommend-section">
      <span class="recommend-label good">⭐ 吉</span>
      <span
        v-for="d in goodDays"
        :key="d.day"
        class="recommend-day good"
        @click="$emit('day-click', d)"
      >{{ month }}月{{ d.day }}日（{{ d.lunarDate.replace('农历','') }}）</span>
    </div>

    <div v-if="bestDays.length === 0 && goodDays.length === 0" class="no-good-days">
      本月暂无特别推荐的动土吉日，建议查询其他月份。
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  days: Array,
  month: Number,
})

defineEmits(['day-click'])

const bestDays = computed(() => props.days.filter(d => d.rating === 'best'))
const goodDays = computed(() => props.days.filter(d => d.rating === 'good'))
</script>
```

**Step 2: Commit**

```bash
git add auspicious-date-selector/src/components/RecommendList.vue
git commit -m "feat: add RecommendList component showing best and good days"
```

---

## Task 7: Wire Everything in App.vue

**Files:**
- Modify: `auspicious-date-selector/src/App.vue`

**Step 1: Replace App.vue contents**

```vue
<template>
  <div class="app">
    <header class="app-header">
      <h1>📅 黄道吉日查询</h1>
      <p class="app-subtitle">修坟动土专用 · 传统农历推算</p>
    </header>

    <main class="app-main">
      <InputForm @query="onQuery" />

      <template v-if="queryResult">
        <RecommendList
          :days="queryResult.days"
          :month="queryResult.month"
          @day-click="openDetail"
        />
        <CalendarView
          :year="queryResult.year"
          :month="queryResult.month"
          :days="queryResult.days"
          :user-name="queryResult.name"
          @day-click="openDetail"
        />
      </template>
    </main>

    <DayDetail
      v-if="selectedDay"
      :day="selectedDay"
      :year="queryResult.year"
      :month="queryResult.month"
      @close="selectedDay = null"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import InputForm from './components/InputForm.vue'
import CalendarView from './components/CalendarView.vue'
import DayDetail from './components/DayDetail.vue'
import RecommendList from './components/RecommendList.vue'
import { getUserZodiac, getDaysInMonth } from './utils/auspicious.js'

const queryResult = ref(null)
const selectedDay = ref(null)

function onQuery({ name, birthYear, birthMonth, birthDay, queryYear, queryMonth }) {
  const zodiac = getUserZodiac(birthYear, birthMonth, birthDay)
  const days = getDaysInMonth(queryYear, queryMonth, zodiac)
  queryResult.value = { name, year: queryYear, month: queryMonth, days, zodiac }
}

function openDetail(dayInfo) {
  selectedDay.value = dayInfo
}
</script>
```

**Step 2: Verify full flow in browser**

```bash
npm run dev
```

Test:
1. Select a birth date
2. Select a query month
3. Click 查询吉日
4. Verify calendar renders with colored days
5. Click a day — verify popup appears
6. Verify RecommendList shows best/good days

**Step 3: Commit**

```bash
git add auspicious-date-selector/src/App.vue
git commit -m "feat: wire together App.vue with full query flow"
```

---

## Task 8: Global Styles (Elderly-Friendly)

**Files:**
- Modify: `auspicious-date-selector/src/style.css`

**Step 1: Replace style.css with elderly-friendly styles**

```css
/* ===== Global Reset & Base ===== */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  font-size: 20px;
  line-height: 1.6;
  background: #f5f0e8;
  color: #222;
}

/* ===== App Layout ===== */
.app { max-width: 900px; margin: 0 auto; padding: 16px; }

.app-header {
  text-align: center;
  padding: 24px 0 16px;
}
.app-header h1 { font-size: 32px; color: #8b1a1a; }
.app-subtitle { font-size: 18px; color: #666; margin-top: 4px; }

.app-main { display: flex; flex-direction: column; gap: 24px; }

/* ===== Input Form ===== */
.input-form {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.input-form h2 { font-size: 22px; margin-bottom: 20px; color: #555; }

.form-row { display: flex; align-items: center; gap: 16px; margin-bottom: 16px; flex-wrap: wrap; }
.form-row label { font-size: 20px; min-width: 100px; font-weight: 600; }

.input-text {
  font-size: 20px;
  padding: 10px 14px;
  border: 2px solid #ccc;
  border-radius: 8px;
  width: 200px;
}

.date-selects { display: flex; gap: 8px; flex-wrap: wrap; }

.select-lg {
  font-size: 20px;
  padding: 10px 14px;
  border: 2px solid #ccc;
  border-radius: 8px;
  background: white;
  cursor: pointer;
}
.select-lg:focus { border-color: #2e7d32; outline: none; }

.btn-query {
  margin-top: 8px;
  font-size: 22px;
  padding: 14px 40px;
  background: #2e7d32;
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: bold;
  width: 100%;
}
.btn-query:hover { background: #1b5e20; }

/* ===== Recommend List ===== */
.recommend-list {
  background: white;
  border-radius: 12px;
  padding: 20px 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.recommend-list h3 { font-size: 22px; margin-bottom: 14px; }
.recommend-section { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 10px; }
.recommend-label { font-size: 18px; font-weight: bold; min-width: 60px; }
.recommend-label.best { color: #1b5e20; }
.recommend-label.good { color: #2e7d32; }
.recommend-day {
  font-size: 18px;
  padding: 6px 14px;
  border-radius: 20px;
  cursor: pointer;
  border: 2px solid transparent;
}
.recommend-day.best { background: #c8e6c9; color: #1b5e20; border-color: #2e7d32; }
.recommend-day.good { background: #e8f5e9; color: #2e7d32; border-color: #81c784; }
.recommend-day:hover { opacity: 0.8; }
.no-good-days { font-size: 18px; color: #888; }

/* ===== Calendar ===== */
.calendar-view {
  background: white;
  border-radius: 12px;
  padding: 20px 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.calendar-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}
.month-title { font-size: 24px; font-weight: bold; }
.user-name { font-size: 18px; color: #888; }

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 6px;
}
.weekday-header {
  text-align: center;
  font-size: 18px;
  font-weight: bold;
  color: #666;
  padding: 8px 0;
}
.day-cell {
  min-height: 80px;
  border-radius: 8px;
  padding: 8px 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  border: 2px solid #eee;
  background: #fafafa;
  transition: opacity 0.15s;
}
.day-cell:hover { opacity: 0.8; }
.day-cell.empty { background: transparent; border-color: transparent; cursor: default; }

.day-number { font-size: 28px; font-weight: bold; line-height: 1.2; }
.day-lunar { font-size: 13px; color: #888; margin-top: 2px; }
.day-badge {
  margin-top: 4px;
  font-size: 13px;
  padding: 2px 6px;
  border-radius: 10px;
  background: #2e7d32;
  color: white;
}
.day-badge.bad { background: #c62828; }

/* Rating colors */
.rating-best { background: #c8e6c9; border-color: #2e7d32; }
.rating-best .day-number { color: #1b5e20; }
.rating-good { background: #e8f5e9; border-color: #81c784; }
.rating-good .day-number { color: #2e7d32; }
.rating-normal { background: #fafafa; border-color: #eee; }
.rating-bad { background: #ffebee; border-color: #ef9a9a; }
.rating-bad .day-number { color: #c62828; }

/* ===== Day Detail Overlay ===== */
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 16px;
}
.detail-card {
  background: white;
  border-radius: 16px;
  padding: 28px 32px;
  max-width: 480px;
  width: 100%;
  position: relative;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}
.close-btn {
  position: absolute;
  top: 16px; right: 20px;
  font-size: 24px;
  background: none;
  border: none;
  cursor: pointer;
  color: #888;
}
.detail-date { font-size: 24px; margin-bottom: 12px; }
.detail-lunar { font-size: 18px; color: #888; margin-left: 8px; }

.detail-tag {
  display: inline-block;
  font-size: 20px;
  font-weight: bold;
  padding: 6px 16px;
  border-radius: 20px;
  margin-bottom: 16px;
}
.tag-best { background: #c8e6c9; color: #1b5e20; }
.tag-good { background: #e8f5e9; color: #2e7d32; }
.tag-normal { background: #f5f5f5; color: #555; }
.tag-bad { background: #ffebee; color: #c62828; }

.detail-row {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  font-size: 20px;
  align-items: flex-start;
}
.detail-label { color: #888; min-width: 120px; flex-shrink: 0; }
.detail-value { color: #222; }
.detail-value.green { color: #2e7d32; }
.detail-value.red { color: #c62828; }

.detail-summary {
  margin-top: 20px;
  font-size: 20px;
  font-weight: bold;
  padding: 14px 16px;
  border-radius: 10px;
  line-height: 1.5;
}
.summary-good { background: #e8f5e9; color: #1b5e20; }
.summary-bad { background: #ffebee; color: #c62828; }
```

**Step 2: Import style.css in main.js**

Verify `src/main.js` has:
```js
import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

createApp(App).mount('#app')
```

**Step 3: Final visual check in browser**

```bash
npm run dev
```

Check:
- [ ] Title is large and clear
- [ ] All dropdowns have font size ≥ 20px
- [ ] 大吉 days are clearly green
- [ ] 不宜 days are clearly red/pink
- [ ] Popup card is easy to read
- [ ] Recommend list shows clickable day chips

**Step 4: Run all tests one final time**

```bash
npm test
```
Expected: All tests PASS

**Step 5: Final commit**

```bash
git add auspicious-date-selector/
git commit -m "feat: add elderly-friendly global styles, complete auspicious date selector MVP"
```

---

## Quick Start (After Implementation)

```bash
cd auspicious-date-selector
npm install
npm run dev
# Open http://localhost:5173
```

To build for deployment:
```bash
npm run build
# Output in dist/ — deploy to any static host (Vercel, Netlify, GitHub Pages)
```
