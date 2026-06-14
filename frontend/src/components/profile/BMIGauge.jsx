// BMI gauge: speedometer-style SVG matching the reference image
export default function BMIGauge({ weight, height, age, t }) {
  if (!weight || !height || weight <= 0 || height <= 0) return null

  const h = height / 100
  const bmi = weight / (h * h)
  const bmiDisplay = bmi.toFixed(1)

  // ── Layout constants ────────────────────────────────────────────────────────
  const CX = 150, CY = 162
  const OR = 128, IR = 78   // outer/inner radius of the gauge ring
  const NL = 118             // needle length from center
  const BMI_MIN = 16, BMI_MAX = 40

  // ── Helpers ─────────────────────────────────────────────────────────────────
  // Map a BMI value → gauge angle in "math" degrees (0=right, 90=top, 180=left)
  function bmiToAngle(b) {
    const clamped = Math.min(Math.max(b, BMI_MIN), BMI_MAX)
    return (1 - (clamped - BMI_MIN) / (BMI_MAX - BMI_MIN)) * 180
  }

  // Convert angle + radius → SVG x,y (standard math convention, y flipped for SVG)
  function polar(r, angleDeg) {
    const rad = (angleDeg * Math.PI) / 180
    return [
      +(CX + r * Math.cos(rad)).toFixed(3),
      +(CY - r * Math.sin(rad)).toFixed(3),
    ]
  }

  // Build the SVG path for a donut ring segment from one BMI value to another
  function ringPath(fromBMI, toBMI) {
    const a1 = bmiToAngle(fromBMI)  // start angle (larger = more left)
    const a2 = bmiToAngle(toBMI)    // end angle   (smaller = more right)
    if (Math.abs(a1 - a2) < 0.01) return ''

    const [ox1, oy1] = polar(OR, a1)
    const [ox2, oy2] = polar(OR, a2)
    const [ix2, iy2] = polar(IR, a2)
    const [ix1, iy1] = polar(IR, a1)

    // sweep=1 draws CW (over the top), sweep=0 draws CCW (return arc)
    return [
      `M ${ox1} ${oy1}`,
      `A ${OR} ${OR} 0 0 1 ${ox2} ${oy2}`,
      `L ${ix2} ${iy2}`,
      `A ${IR} ${IR} 0 0 0 ${ix1} ${iy1}`,
      'Z',
    ].join(' ')
  }

  // ── Zone definitions ────────────────────────────────────────────────────────
  const ZONES = [
    { from: 16,   to: 17,   color: '#7f1d1d' },  // severely underweight
    { from: 17,   to: 18.5, color: '#ef4444' },  // underweight
    { from: 18.5, to: 25,   color: '#16a34a' },  // normal
    { from: 25,   to: 30,   color: '#ca8a04' },  // overweight
    { from: 30,   to: 35,   color: '#f97316' },  // obese I
    { from: 35,   to: 40,   color: '#b91c1c' },  // obese II+
  ]

  // Zone labels placed at the midpoint of each labelled zone
  const ZONE_LABELS = [
    { midBMI: 17.25, text: 'Underweight' },
    { midBMI: 21.75, text: 'Normal' },
    { midBMI: 27.5,  text: 'Overweight' },
    { midBMI: 35,    text: 'Obesity' },
  ]

  // Tick positions
  const TICKS = [16, 17, 18.5, 25, 30, 35, 40]

  // ── Current BMI info ────────────────────────────────────────────────────────
  function getCategory(b) {
    if (b < 17)   return { labelKey: 'bmi_cat_sev_under', label: 'Severely Underweight', color: '#7f1d1d' }
    if (b < 18.5) return { labelKey: 'bmi_cat_under',     label: 'Underweight',          color: '#ef4444' }
    if (b < 25)   return { labelKey: 'bmi_cat_normal',    label: 'Normal weight',        color: '#16a34a' }
    if (b < 30)   return { labelKey: 'bmi_cat_over',      label: 'Overweight',           color: '#ca8a04' }
    if (b < 35)   return { labelKey: 'bmi_cat_obese1',    label: 'Obese (Class I)',      color: '#f97316' }
    return          { labelKey: 'bmi_cat_obese2',    label: 'Obese (Class II+)',    color: '#b91c1c' }
  }

  const cat = getCategory(bmi)
  const catLabel = t?.[cat.labelKey] || cat.label

  // Healthy weight range (BMI 18.5–25)
  const minHealthy = (18.5 * h * h).toFixed(1)
  const maxHealthy = (25 * h * h).toFixed(1)
  const weightDiff = bmi < 18.5
    ? (18.5 * h * h - weight).toFixed(1)
    : bmi >= 25
      ? (weight - 25 * h * h).toFixed(1)
      : null

  const bmiPrime = (bmi / 25).toFixed(2)

  // Needle coordinates
  const needleAngle = bmiToAngle(bmi)
  const [nx, ny] = polar(NL, needleAngle)

  return (
    <div className="bmi-gauge-wrap">
      <h3 className="bmi-gauge-heading">📊 {t?.bmi_title || 'BMI Analysis'}</h3>

      {/* ── Gauge header label ─────────────────────────────────────────────── */}
      <p className="bmi-category-label" style={{ color: cat.color }}>
        BMI = {bmiDisplay} kg/m²
        <span className="bmi-category-tag" style={{ background: cat.color }}>
          {catLabel}
        </span>
      </p>

      {/* ── SVG speedometer ───────────────────────────────────────────────── */}
      <svg
        viewBox="0 0 300 185"
        className="bmi-gauge-svg"
        role="img"
        aria-label={`BMI gauge showing ${bmiDisplay}`}
      >
        {/* Zone arc segments */}
        {ZONES.map((z, i) => (
          <path key={i} d={ringPath(z.from, z.to)} fill={z.color} />
        ))}

        {/* Gap lines between zones (thin white lines at each BMI boundary) */}
        {[17, 18.5, 25, 30, 35].map((b) => {
          const a = bmiToAngle(b)
          const [x1, y1] = polar(IR - 1, a)
          const [x2, y2] = polar(OR + 1, a)
          return (
            <line key={b} x1={x1} y1={y1} x2={x2} y2={y2}
              stroke="var(--bg-card)" strokeWidth={1.5} />
          )
        })}

        {/* Zone labels inside the ring */}
        {ZONE_LABELS.map((l, i) => {
          const a = bmiToAngle(l.midBMI)
          const midR = (OR + IR) / 2
          const [tx, ty] = polar(midR, a)
          const rotation = -(90 - a)  // tangent to the arc
          return (
            <text
              key={i}
              x={tx}
              y={ty}
              textAnchor="middle"
              dominantBaseline="middle"
              fontSize={8.5}
              fontWeight="700"
              fill="white"
              transform={`rotate(${rotation.toFixed(1)}, ${tx}, ${ty})`}
            >
              {l.text}
            </text>
          )
        })}

        {/* Tick marks at key BMI values */}
        {TICKS.map((b) => {
          const a = bmiToAngle(b)
          const [tx1, ty1] = polar(OR + 1, a)
          const [tx2, ty2] = polar(OR + 10, a)
          const [lx, ly] = polar(OR + 21, a)
          const isKey = [18.5, 25, 30, 35].includes(b)
          return (
            <g key={b}>
              <line x1={tx1} y1={ty1} x2={tx2} y2={ty2}
                stroke="var(--text)" strokeWidth={isKey ? 2 : 1.2} opacity={0.7} />
              <text
                x={lx} y={ly}
                textAnchor="middle"
                dominantBaseline="middle"
                fontSize={isKey ? 9 : 7.5}
                fontWeight={isKey ? 700 : 500}
                fill="var(--text)"
                opacity={0.85}
              >
                {b}
              </text>
            </g>
          )
        })}

        {/* Needle */}
        <line
          x1={CX} y1={CY}
          x2={nx} y2={ny}
          stroke="var(--text)"
          strokeWidth={2.5}
          strokeLinecap="round"
        />
        {/* Needle base circles */}
        <circle cx={CX} cy={CY} r={9} fill="var(--text)" opacity={0.9} />
        <circle cx={CX} cy={CY} r={5.5} fill="var(--bg-card)" />

        {/* BMI value + category inside the arc */}
        <text
          x={CX}
          y={CY - 38}
          textAnchor="middle"
          fontSize={28}
          fontWeight="800"
          fill="var(--text)"
        >
          {bmiDisplay}
        </text>
        <text
          x={CX}
          y={CY - 16}
          textAnchor="middle"
          fontSize={10}
          fill="var(--text-subtle)"
        >
          kg/m²
        </text>
      </svg>

      {/* ── Info rows ────────────────────────────────────────────────────────── */}
      <ul className="bmi-info-list">
        <li className="bmi-info-row">
          <span className="bmi-info-label">{t?.bmi_healthy_range || 'Healthy weight range'}</span>
          <span className="bmi-info-value">{minHealthy} – {maxHealthy} kg</span>
        </li>
        {weightDiff !== null && (
          <li className="bmi-info-row">
            <span className="bmi-info-label">
              {bmi < 18.5
                ? (t?.bmi_gain || 'Gain to reach healthy')
                : (t?.bmi_lose || 'Lose to reach healthy')}
            </span>
            <span className="bmi-info-value" style={{ color: cat.color }}>
              {weightDiff} kg
            </span>
          </li>
        )}
        <li className="bmi-info-row">
          <span className="bmi-info-label">{t?.bmi_prime || 'BMI Prime'}</span>
          <span className="bmi-info-value">{bmiPrime}</span>
        </li>
        {age && (
          <li className="bmi-info-row">
            <span className="bmi-info-label">{t?.bmi_age || 'Age'}</span>
            <span className="bmi-info-value">{age} yrs</span>
          </li>
        )}
      </ul>
    </div>
  )
}
