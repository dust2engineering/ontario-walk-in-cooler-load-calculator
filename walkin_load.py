#!/usr/bin/env python3
"""Walk-in cooler/freezer refrigeration load quick calculator (Heatcraft method).
Usage:
  python3 walkin_load.py --length 10 --width 8 --height 8 --box-temp 35 --ambient 90 \
      --material "Foamed-in-place polyurethane" --thickness 4 --product Milk --lb-per-day 500 --entering-temp 70
All dimensions in feet, temperatures in F. See --help for the rest.
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
# The calculation lives in this file (self-contained copy of the verified method).
import math
K = {"Foamed-in-place polyurethane": 0.16, "Sprayed polyurethane": 0.12, "Polystyrene (Styrofoam)": 0.24, "Cork": 0.38, "Mineral wool": 0.30}
AC = [(200,44.0,33.5),(250,38.0,29.0),(300,34.5,26.2),(400,29.5,22.5),(500,26.0,20.0),(600,23.0,18.0),(800,20.0,15.3),(1000,17.5,13.5),(1500,14.0,11.0),(2000,12.0,9.3),(3000,9.5,7.4),(4000,8.2,6.3),(5000,7.2,5.6),(6000,6.5,5.0),(8000,5.5,4.3),(10000,4.9,3.8),(15000,3.9,3.0),(20000,3.5,2.6),(25000,3.0,2.3),(30000,2.7,2.1),(40000,2.3,1.8),(50000,2.0,1.6),(75000,1.6,1.3),(100000,1.4,1.1),(150000,1.2,1.0),(200000,1.1,0.9),(300000,1.0,0.85)]
PROD = {"Apples":(29.3,0.87,0.45,121),"Beef (fresh)":(28.5,0.77,0.41,100),"Pork (fresh)":(28.5,0.51,0.32,55),"Lamb (fresh)":(28.5,0.72,0.45,93),"Chicken (fresh)":(27.0,0.79,0.42,106),"Fish (fresh)":(28.0,0.78,0.42,101),"Milk":(31.0,0.93,0.49,124),"Eggs (in shell)":(28.0,0.73,0.40,96),"Ice cream":(21.0,0.68,0.38,86),"Mixed vegetables":(30.0,0.90,0.45,130),"Generic (Heatcraft quick default)":(27.0,0.80,0.45,100)}
PPL = [(50,17280),(40,20160),(30,22800),(20,25200),(10,28800),(0,31200),(-10,33600)]
def interp(x, pts):
    if x <= pts[0][0]: return pts[0][1]
    if x >= pts[-1][0]: return pts[-1][1]
    for i in range(len(pts)-1):
        if pts[i][0] <= x <= pts[i+1][0]:
            f = (x-pts[i][0])/(pts[i+1][0]-pts[i][0]); return pts[i][1]+f*(pts[i+1][1]-pts[i][1])
def sat_w(tf):
    tc = (tf-32)*5/9
    p = 0.61094*math.exp(17.625*tc/(tc+243.04)) if tc >= 0 else 0.61115*math.exp(22.452*tc/(tc+272.55))
    return 0.621945*p/(101.325-p)
def enth(tf, w): return 0.240*tf + w*(1061+0.444*tf)
def heat_ft3(amb, rh, box):
    dh = enth(amb, rh*sat_w(amb)) - enth(box, sat_w(box))
    return dh * (144*14.696/(53.35*(box+459.67)))
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--length", type=float, required=True); ap.add_argument("--width", type=float, required=True); ap.add_argument("--height", type=float, required=True)
    ap.add_argument("--box-temp", type=float, required=True); ap.add_argument("--ambient", type=float, default=90)
    ap.add_argument("--material", choices=list(K), default="Foamed-in-place polyurethane"); ap.add_argument("--thickness", type=float, default=4)
    ap.add_argument("--usage", choices=["normal", "heavy", "long-term storage"], default="normal")
    ap.add_argument("--product", choices=list(PROD), default="Generic (Heatcraft quick default)")
    ap.add_argument("--lb-per-day", type=float, default=0); ap.add_argument("--entering-temp", type=float, default=70)
    ap.add_argument("--pulldown-hours", type=float, default=24)
    ap.add_argument("--motor-hp", type=float, default=0); ap.add_argument("--lights-w", type=float, default=0); ap.add_argument("--lights-hours", type=float, default=24)
    ap.add_argument("--people", type=float, default=0); ap.add_argument("--people-hours", type=float, default=0)
    ap.add_argument("--glass-doors", type=int, default=0); ap.add_argument("--ambient-rh", type=float, default=0.5)
    ap.add_argument("--run-hours", type=float, default=None)
    a = ap.parse_args()
    U = K[a.material]/a.thickness
    wall = 2*(a.length*a.height + a.width*a.height); ca = a.length*a.width
    q_tr = U*(wall*(a.ambient-a.box_temp) + ca*(a.ambient-a.box_temp) + ca*(55-a.box_temp))*24
    vol = a.length*a.width*a.height
    ac = interp(vol, [(v, ab if a.box_temp > 32 else be) for v, ab, be in AC])
    uf = {"normal": 1.0, "heavy": 2.0, "long-term storage": 0.6}[a.usage]
    q_inf = vol*ac*uf*heat_ft3(a.ambient, a.ambient_rh, a.box_temp)
    fp, cpa, cpb, lat = PROD[a.product]; q_pr = 0.0
    if a.lb_per_day > 0 and a.entering_temp > a.box_temp:
        if a.box_temp >= fp: q = a.lb_per_day*cpa*(a.entering_temp-a.box_temp)
        elif a.entering_temp >= fp: q = a.lb_per_day*cpa*(a.entering_temp-fp) + a.lb_per_day*lat + a.lb_per_day*cpb*(fp-a.box_temp)
        else: q = a.lb_per_day*cpb*(a.entering_temp-a.box_temp)
        q_pr = q*(24/a.pulldown_hours if a.pulldown_hours > 0 else 1)
    q_mo = a.motor_hp*75000; q_li = a.lights_w*3.41*a.lights_hours
    q_pe = a.people*interp(a.box_temp, sorted(PPL))*(a.people_hours/24); q_do = a.glass_doors*31200
    sub = q_tr+q_inf+q_pr+q_mo+q_li+q_pe+q_do; tot = sub*1.10
    run = a.run_hours if a.run_hours else (18 if a.box_temp < 32 else 16)
    for label, v in [("Transmission", q_tr), ("Infiltration", q_inf), ("Product", q_pr), ("Motors", q_mo), ("Lights", q_li), ("People", q_pe), ("Glass doors", q_do)]:
        print(f"{label:14s} {round(v):>10,} BTU/24h")
    print(f"{'Subtotal':14s} {round(sub):>10,} BTU/24h")
    print(f"{'Total (+10%)':14s} {round(tot):>10,} BTU/24h")
    print(f"Required capacity at {run:g} h run time: {round(tot/run):,} BTUH")
if __name__ == "__main__":
    main()
