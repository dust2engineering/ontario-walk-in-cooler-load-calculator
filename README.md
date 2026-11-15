# Walk-In Cooler / Freezer Load Quick Calculator (Heatcraft Method)

A quick refrigeration load estimate for walk-in coolers and freezers using the Heatcraft engineering-manual method: transmission through insulated panels, infiltration from air-change tables, product pull-down and freezing loads, and internal loads (motors, lights, people, glass doors), with the manual's 10% safety factor and a run-time conversion to required BTUH.

**Live web tool:** https://dust2engineering.github.io/ontario-walk-in-cooler-load-calculator/web/

## How it works

- Transmission: U = k / insulation thickness, using the manual's published k values (foamed-in-place polyurethane 0.16, sprayed polyurethane 0.12, polystyrene 0.24, cork 0.38, mineral wool 0.30 BTU·in/hr·ft²·°F); floor is taken against 55 °F ground.
- Infiltration: air changes per 24 h from the manual's volume tables (separate tables above and below 32 °F), ×2 for heavy use, ×0.6 for long-term storage; the heat per cubic foot is computed psychrometrically by the Table 6 method.
- Product: sensible heat above freezing, latent heat of freezing, and sensible heat below freezing from Table 7 properties; a pull-down shorter than 24 h scales the load by 24/hours.
- Internal: motors 75,000 BTU/HP/24h (quick formula), lights at 3.41 BTU/Wh, people by box temperature, glass doors 31,200 BTU/door/24h; then +10% safety, divided by run hours (18 h freezer / 16 h cooler convention).

## Data in this repository

- `walk-in-load-data.json` — k values, the full air-change tables, product properties, internal-load factors and the thickness recommendations, as machine-readable JSON.
- All factors verified from the Heatcraft Engineering Manual H-ENGM0408. Two honesty limits: the manual's Table 6 per-cell values were not legible in any public copy, so infiltration heat per ft³ is computed (it reproduces the manual's worked anchor, 85 °F ambient / −20 °F box ≈ 3.49 BTU/ft³); and respiration heat for fresh produce is not included, because no verified table was available.

## Command line

```bash
python3 walkin_load.py --length 10 --width 8 --height 8 --box-temp 35 --ambient 90 --product Milk --lb-per-day 500 --entering-temp 70
```

## Worked examples

- [example-dairy-cooler.txt](examples/example-dairy-cooler.txt)
- [example-freezer.txt](examples/example-freezer.txt)

## Scope and limits

Preliminary design aid only. It does not replace the current Ontario Building Code, the Canadian Electrical Code or CSA B149.1, or the judgement of the designer of record. Verify all values against the Code in force for your project before submitting drawings for permit.

## About

Maintained by **Dust 2 Engineering Inc.** (Mississauga, Ontario) — building permit drawings
(architectural, HVAC, plumbing, sprinkler, electrical) for restaurants and small commercial
projects across the Greater Toronto Area, stamped by an Ontario P.Eng. Flat rate $3,500–$5,000.

Category: HVAC / mechanical. More free Ontario code tools: see the full index at
https://github.com/dust2engineering
