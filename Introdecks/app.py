import streamlit as st
import sqlite3
import pandas as pd
import zipfile
from pathlib import Path
from datetime import date
import os

# Project directory
base = Path(__file__).resolve().parent
base.mkdir(parents=True, exist_ok=True)

# Database location
DB_PATH = base / "insurance.db"

st.set_page_config(page_title="InsureFlow | Insurance Management", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
html, body, [class*="css"] {font-family:'DM Sans',sans-serif}
.stApp{background:#f5f7fb}
.block-container{padding-top:1.5rem;max-width:1450px}
[data-testid="stSidebar"]{background:#101c35}
[data-testid="stSidebar"] *{color:#eef3ff!important}
h1,h2,h3{font-family:'Manrope',sans-serif!important;color:#14213d}
.hero{background:linear-gradient(115deg,#14213d,#234b78 60%,#287c91);padding:28px 32px;border-radius:18px;color:white;margin-bottom:22px}
.hero h1{color:white!important;font-size:2rem;margin:0 0 6px}
.hero p{color:#dce9f8;margin:0}
.metric{background:white;border:1px solid #e8edf5;border-radius:15px;padding:18px 20px;box-shadow:0 4px 16px #1a2e500b}
.metric-label{color:#718096;font-size:.82rem;font-weight:600}
.metric-value{color:#152541;font-family:'Manrope';font-size:1.7rem;font-weight:800;margin-top:5px}
.metric-note{color:#8290a5;font-size:.76rem}
</style>
""", unsafe_allow_html=True)

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    return con

def run(sql, params=()):
    with db() as con:
        cur = con.execute(sql, params)
        con.commit()
        return cur.lastrowid

def read(sql, params=()):
    with db() as con:
        return pd.read_sql_query(sql, con, params=params)

def premium(policy_type, amount, risk):
    rates = {"Life": .01, "Vehicle": .015, "Health": .02}
    factors = {"Low": .9, "Medium": 1.0, "High": 1.4}
    return round(float(amount) * rates[policy_type] * factors[risk], 2)

def money(x):
    return f"₹{float(x or 0):,.0f}"

def setup():
    with db() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS policyholders(
            holder_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, phone TEXT, email TEXT, city TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS policies(
            policy_id INTEGER PRIMARY KEY AUTOINCREMENT,
            holder_id INTEGER NOT NULL,
            policy_type TEXT NOT NULL,
            sum_insured REAL NOT NULL CHECK(sum_insured>0),
            risk_level TEXT NOT NULL,
            premium REAL NOT NULL,
            policy_status TEXT NOT NULL DEFAULT 'Active',
            start_date TEXT NOT NULL,
            FOREIGN KEY(holder_id) REFERENCES policyholders(holder_id)
        );
        CREATE TABLE IF NOT EXISTS claims(
            claim_id INTEGER PRIMARY KEY AUTOINCREMENT,
            policy_id INTEGER NOT NULL,
            claim_amount REAL NOT NULL CHECK(claim_amount>0),
            claim_reason TEXT,
            claim_status TEXT NOT NULL DEFAULT 'Pending',
            claim_date TEXT NOT NULL,
            FOREIGN KEY(policy_id) REFERENCES policies(policy_id)
        );
        CREATE TABLE IF NOT EXISTS payments(
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            policy_id INTEGER NOT NULL,
            amount REAL NOT NULL CHECK(amount>0),
            payment_method TEXT NOT NULL,
            payment_date TEXT NOT NULL,
            payment_status TEXT NOT NULL DEFAULT 'Paid',
            FOREIGN KEY(policy_id) REFERENCES policies(policy_id)
        );
        """)
        if con.execute("SELECT COUNT(*) FROM policyholders").fetchone()[0] == 0:
            con.executemany("INSERT INTO policyholders(name,phone,email,city) VALUES(?,?,?,?)", [
                ("Aarav Sharma","9876543210","aarav@example.com","Chandigarh"),
                ("Meera Kapoor","9876501234","meera@example.com","Mohali"),
                ("Kabir Verma","9812345670","kabir@example.com","Kharar"),
                ("Ananya Gill","9898765432","ananya@example.com","Panchkula"),
            ])
            today = date.today().isoformat()
            con.executemany("""INSERT INTO policies
                (holder_id,policy_type,sum_insured,risk_level,premium,policy_status,start_date)
                VALUES(?,?,?,?,?,?,?)""", [
                (1,"Health",500000,"High",14000,"Active",today),
                (2,"Life",1000000,"Low",9000,"Active",today),
                (3,"Vehicle",400000,"Medium",6000,"Active",today),
                (4,"Health",300000,"Medium",6000,"Active",today),
            ])
            con.executemany("""INSERT INTO claims
                (policy_id,claim_amount,claim_reason,claim_status,claim_date)
                VALUES(?,?,?,?,?)""", [
                (1,25000,"Hospital treatment","Pending",today),
                (2,50000,"Family benefit claim","Approved",today),
            ])
            con.executemany("""INSERT INTO payments
                (policy_id,amount,payment_method,payment_date,payment_status)
                VALUES(?,?,?,?,?)""", [
                (1,14000,"UPI",today,"Paid"),
                (2,9000,"Card",today,"Paid"),
                (3,6000,"UPI",today,"Paid"),
            ])

setup()

holders = read("SELECT * FROM policyholders ORDER BY holder_id DESC")
policies = read("""SELECT p.*,h.name AS holder_name FROM policies p
                   JOIN policyholders h ON p.holder_id=h.holder_id ORDER BY p.policy_id DESC""")
claims = read("""SELECT c.*,h.name AS holder_name,p.policy_type FROM claims c
                 JOIN policies p ON c.policy_id=p.policy_id
                 JOIN policyholders h ON p.holder_id=h.holder_id ORDER BY c.claim_id DESC""")
payments = read("""SELECT x.*,h.name AS holder_name,p.policy_type FROM payments x
                   JOIN policies p ON x.policy_id=p.policy_id
                   JOIN policyholders h ON p.holder_id=h.holder_id ORDER BY x.payment_id DESC""")

with st.sidebar:
    st.markdown("## 🛡️ InsureFlow")
    st.caption("INSURANCE MANAGEMENT")
    page = st.radio("NAVIGATION", ["Overview","Policyholders","Policies","Claims","Payments"], label_visibility="collapsed")
    st.divider()
    st.caption("DBMS MINI PROJECT")
    st.caption("Python · Streamlit · SQLite")

st.markdown("""<div class="hero"><h1>Insurance Policy Management</h1>
<p>Manage customers, policies, premiums, claims and payments in one place.</p></div>""", unsafe_allow_html=True)

if page == "Overview":
    active = int((policies.policy_status == "Active").sum()) if not policies.empty else 0
    collected = payments.loc[payments.payment_status=="Paid","amount"].sum() if not payments.empty else 0
    pending = int((claims.claim_status=="Pending").sum()) if not claims.empty else 0
    metrics = [("Policyholders",len(holders),"Registered customers"),("Active policies",active,f"{len(policies)} total policies"),("Premium collected",money(collected),"Successful payments"),("Pending claims",pending,"Awaiting review")]
    cols = st.columns(4)
    for col,(label,value,note) in zip(cols,metrics):
        col.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',unsafe_allow_html=True)
    st.write("")
    a,b=st.columns([1.2,1])
    with a:
        st.subheader("Policy portfolio")
        if not policies.empty: st.bar_chart(policies.groupby("policy_type").size().rename("Policies"),color="#287c91")
        else: st.info("No policies yet.")
    with b:
        st.subheader("Claims snapshot")
        if not claims.empty: st.bar_chart(claims.groupby("claim_status").size().rename("Claims"),color="#5b8f78")
        else: st.info("No claims yet.")
    st.subheader("Recent policies")
    if not policies.empty:
        st.dataframe(policies[["policy_id","holder_name","policy_type","sum_insured","risk_level","premium","policy_status"]].rename(columns={"policy_id":"Policy ID","holder_name":"Policyholder","policy_type":"Type","sum_insured":"Sum insured (₹)","risk_level":"Risk","premium":"Premium (₹)","policy_status":"Status"}),use_container_width=True,hide_index=True)

elif page == "Policyholders":
    st.subheader("Policyholders")
    st.caption("Register and manage insurance customers.")
    with st.expander("＋ Add policyholder"):
        with st.form("holder_form",clear_on_submit=True):
            c1,c2=st.columns(2)
            name=c1.text_input("Full name *"); phone=c2.text_input("Phone")
            email=c1.text_input("Email"); city=c2.text_input("City")
            if st.form_submit_button("Save policyholder",type="primary"):
                if not name.strip(): st.error("Name is required.")
                else:
                    run("INSERT INTO policyholders(name,phone,email,city) VALUES(?,?,?,?)",(name.strip(),phone,email,city))
                    st.success("Policyholder added."); st.rerun()
    if not holders.empty:
        st.dataframe(holders[["holder_id","name","phone","email","city"]].rename(columns={"holder_id":"ID","name":"Name","phone":"Phone","email":"Email","city":"City"}),use_container_width=True,hide_index=True)
        with st.expander("Delete policyholder"):
            st.caption("Deletion is blocked if the customer has linked policies.")
            did=st.selectbox("Customer",holders.holder_id.tolist(),format_func=lambda x:f"#{x} — {holders.loc[holders.holder_id==x,'name'].iloc[0]}")
            if st.button("Delete customer"):
                try: run("DELETE FROM policyholders WHERE holder_id=?",(int(did),)); st.success("Deleted."); st.rerun()
                except sqlite3.IntegrityError: st.error("Customer has linked policies and cannot be deleted.")

elif page == "Policies":
    st.subheader("Insurance policies")
    st.caption("Premium is calculated automatically from policy type, insured amount and risk.")
    options={f"{r['name']} (ID {r['holder_id']})":int(r["holder_id"]) for _,r in holders.iterrows()}
    if not options: st.warning("Add a policyholder first.")
    else:
        with st.expander("＋ Create policy",expanded=True):
            with st.form("policy_form",clear_on_submit=True):
                holder=st.selectbox("Policyholder",list(options))
                c1,c2,c3=st.columns(3)
                typ=c1.selectbox("Policy type",["Health","Life","Vehicle"])
                amount=c2.number_input("Sum insured (₹)",min_value=1000,value=500000,step=10000)
                risk=c3.selectbox("Risk level",["Low","Medium","High"])
                start=st.date_input("Start date",value=date.today())
                premium_value=premium(typ,amount,risk)
                st.info(f"Calculated premium: **{money(premium_value)}**")
                if st.form_submit_button("Create policy",type="primary"):
                    run("""INSERT INTO policies(holder_id,policy_type,sum_insured,risk_level,premium,policy_status,start_date)
                            VALUES(?,?,?,?,?,'Active',?)""",(options[holder],typ,float(amount),risk,premium_value,start.isoformat()))
                    st.success("Policy created."); st.rerun()
    if not policies.empty:
        st.dataframe(policies[["policy_id","holder_name","policy_type","sum_insured","risk_level","premium","policy_status","start_date"]].rename(columns={"policy_id":"Policy ID","holder_name":"Policyholder","policy_type":"Type","sum_insured":"Sum insured (₹)","risk_level":"Risk","premium":"Premium (₹)","policy_status":"Status","start_date":"Start date"}),use_container_width=True,hide_index=True)
        with st.expander("Update policy status"):
            pid=st.selectbox("Policy ID",policies.policy_id.tolist())
            status=st.selectbox("Status",["Active","Expired","Cancelled"])
            if st.button("Update policy"):
                run("UPDATE policies SET policy_status=? WHERE policy_id=?",(status,int(pid))); st.success("Updated."); st.rerun()

elif page == "Claims":
    st.subheader("Claims management")
    st.caption("Register insurance claims and review their status.")
    options={f"Policy #{r['policy_id']} · {r['holder_name']} · {r['policy_type']}":int(r["policy_id"]) for _,r in policies.iterrows()}
    if not options: st.warning("Create a policy first.")
    else:
        with st.expander("＋ Register claim"):
            with st.form("claim_form",clear_on_submit=True):
                policy=st.selectbox("Policy",list(options))
                amount=st.number_input("Claim amount (₹)",min_value=1,value=10000,step=1000)
                reason=st.text_area("Reason")
                day=st.date_input("Claim date",value=date.today())
                if st.form_submit_button("Submit claim",type="primary"):
                    run("INSERT INTO claims(policy_id,claim_amount,claim_reason,claim_status,claim_date) VALUES(?,?,?,'Pending',?)",(options[policy],float(amount),reason,day.isoformat()))
                    st.success("Claim registered as Pending."); st.rerun()
    if not claims.empty:
        st.dataframe(claims[["claim_id","holder_name","policy_type","claim_amount","claim_reason","claim_status","claim_date"]].rename(columns={"claim_id":"Claim ID","holder_name":"Policyholder","policy_type":"Policy","claim_amount":"Amount (₹)","claim_reason":"Reason","claim_status":"Status","claim_date":"Date"}),use_container_width=True,hide_index=True)
        with st.expander("Review claim"):
            cid=st.selectbox("Claim ID",claims.claim_id.tolist())
            status=st.selectbox("Decision",["Pending","Approved","Rejected"])
            if st.button("Save decision"):
                run("UPDATE claims SET claim_status=? WHERE claim_id=?",(status,int(cid))); st.success("Claim updated."); st.rerun()

elif page == "Payments":
    st.subheader("Premium payments")
    st.caption("Record premium payments and track collections.")
    options={f"Policy #{r['policy_id']} · {r['holder_name']} · {money(r['premium'])} premium":int(r["policy_id"]) for _,r in policies.iterrows()}
    if not options: st.warning("Create a policy first.")
    else:
        with st.expander("＋ Record payment"):
            with st.form("payment_form",clear_on_submit=True):
                policy=st.selectbox("Policy",list(options))
                amount=st.number_input("Amount received (₹)",min_value=1,value=5000,step=500)
                method=st.selectbox("Payment method",["UPI","Card","Net banking","Cash"])
                day=st.date_input("Payment date",value=date.today())
                status=st.selectbox("Payment status",["Paid","Pending","Failed"])
                if st.form_submit_button("Save payment",type="primary"):
                    run("INSERT INTO payments(policy_id,amount,payment_method,payment_date,payment_status) VALUES(?,?,?,?,?)",(options[policy],float(amount),method,day.isoformat(),status))
                    st.success("Payment saved."); st.rerun()
    if not payments.empty:
        st.dataframe(payments[["payment_id","holder_name","policy_type","amount","payment_method","payment_date","payment_status"]].rename(columns={"payment_id":"Payment ID","holder_name":"Policyholder","policy_type":"Policy","amount":"Amount (₹)","payment_method":"Method","payment_date":"Date","payment_status":"Status"}),use_container_width=True,hide_index=True)
        st.metric("Total successful payments",money(payments.loc[payments.payment_status=="Paid","amount"].sum()))

st.markdown("---")
st.caption("InsureFlow · DBMS Mini Project · Educational demo only. Premium rates are illustrative, not real insurance pricing.")
