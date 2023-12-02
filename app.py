# Author: Kunal Kumar
# Social: twitter.com/l1v1n9h311, instagram.com/prokunal
# Website: procoder.in
from flask import Flask, render_template,request,redirect,jsonify,session,url_for
from datetime import datetime,timedelta
import sqlite3
import secrets
app = Flask(__name__)


# TODO PROGRAM CODE STARTING
@app.route('/todo',methods=['GET','POST'])
def hello_world():
    if request.method=='POST':
        date_todo = datetime.now().strftime("%I:%M %p %d-%m-%Y")
        title = request.form['title'].upper()
        desc = request.form['desc']
        con = sqlite3.connect("static/track.db")
        cur = con.cursor()
        cur.execute("insert into todo  (title,desc,time) values (?,?,?)",(title,desc,date_todo))
        con.commit()
        con.close()    
    con = sqlite3.connect("static/track.db")
    cur = con.cursor()
    showData = cur.execute("select * from todo where action IS NULL").fetchall()
    doneData = cur.execute("select * from todo where action='done' ORDER BY sno DESC").fetchall()
    con.close()
    return render_template("todo.html",showData=showData,doneData=doneData)

@app.route('/delete/<int:sno>') 
def delete(sno):
    con = sqlite3.connect("static/track.db")
    cur = con.cursor()
    cur.execute("delete from todo where sno=?",(sno,))
    con.commit()
    con.close()
    return redirect("/todo")

@app.route('/update/<int:sno>',methods=['GET','POST']) 
def update(sno):
    if request.method=='POST':
        title = request.form['title'].upper()
        desc = request.form['desc']
        con = sqlite3.connect("static/track.db")
        cur = con.cursor()
        cur.execute("update todo set title = ?,desc = ? where sno = ?",(title,desc,sno))
        con.commit()
        con.close()
        return redirect("/todo")
    con = sqlite3.connect("static/track.db")
    cur = con.cursor()
    data = cur.execute("select * from todo where sno=?",(sno,)).fetchone()
    sno = data[0]
    title = data[1]
    con.close()
    return render_template("update.html",sno=sno,title=title)

@app.route('/done/<int:sno>',methods=['GET','POST']) 
def done(sno):
    con = sqlite3.connect("static/track.db")
    cur = con.cursor()
    cur.execute("update todo set action = 'done' where sno=?",(sno,))
    con.commit()
    con.close()
    return redirect("/todo")
# TODO PROGRAM CODE END       




#TRACKER PROGRAM CODE STARTING 
app.secret_key = secrets.token_hex(16)


@app.route("/", methods=["GET", "POST"])
def setup():
    if request.method == "POST":
        tname = request.form["task_name"]
        exercise = int(request.form["exercise"])
        rest = int(request.form["rest"])
        sets = int(request.form["sets"])

        session["exercise"] = exercise
        session["rest"] = rest
        session["sets"] = sets
        session["set_counter"] = 0
        session["task_name"] = tname
        session["grind_time"] = 0
        session["rest_time"] = 0
        session["unique_name"] = session["task_name"] + "-" + datetime.now().strftime("%H:%M")
        return redirect(url_for("exercise"))
    return render_template("index.html")


@app.route("/rest")
def rest():
    tname=session["task_name"].upper()
    uname = session["unique_name"]
    session["grind_time"] += session["exercise"]
    gtime = session["grind_time"]
    gt_hours, gt_minutes = divmod(gtime, 3600)
    gt_minutes //= 60
    gtime = "{}h {:02d}m".format(gt_hours, gt_minutes)
    session["rest_time"] += session["rest"]
    rtime = session["rest_time"]
    rt_hours, rt_minutes = divmod(rtime, 3600)
    rt_minutes //= 60
    rtime = "{}h {:02d}m".format(rt_hours, rt_minutes)
    set_counter = session["set_counter"]
    sets=session["sets"]
    
    if set_counter == 1:
        exercise_t = session["exercise"]
        start_time = datetime.now()-timedelta(seconds=exercise_t)
        start_time = start_time.strftime("%I:%M %p")
        date_ = datetime.now().strftime("%d-%m-%Y")
        con = sqlite3.connect("static/track.db")
        cur = con.cursor()
        cur.execute("insert into grind values (?,?,?,?,?,?,?,?)",(tname,gtime,rtime,set_counter,date_,uname,start_time,"Pending"))
        con.commit()
        con.close()
    elif set_counter > 1:
        con = sqlite3.connect("static/track.db")
        cur = con.cursor()
        cur.execute("update grind set tspent = ?,rest = ?, sets = ? where uname = ?",(gtime,rtime,set_counter,uname))
        con.commit()
        con.close()
    rest=session["rest"]
    return render_template("rest.html",rest=rest ,task_name=session["task_name"])


@app.route("/exercise")
def exercise():
    set_counter = session["set_counter"]
    sets=session["sets"]
    if set_counter == sets:
         end_time = datetime.now().strftime("%I:%M %p")
         uname = session["unique_name"]
         con = sqlite3.connect("static/track.db")
         cur = con.cursor()
         cur.execute("update grind set end_time = ? where uname = ?",(end_time,uname))
         con.commit()
         con.close()
         return redirect(url_for("completed"))
    session["set_counter"] += 1
    counter=session["set_counter"]
    return render_template("exercise.html", exercise=session["exercise"],name=session["task_name"],sets=sets,counter=counter)

@app.route("/complete")
def completed():
    gtime = session["grind_time"]
    gt_hours, gt_minutes = divmod(gtime, 3600)
    gt_minutes //= 60
    gtime = "{}h {:02d}m".format(gt_hours, gt_minutes)
    rtime = session["rest_time"]
    rt_hours, rt_minutes = divmod(rtime, 3600)
    rt_minutes //= 60
    rtime = "{}h {:02d}m".format(rt_hours, rt_minutes)
    sets=session["set_counter"]
    return render_template("complete.html", sets=sets,gtime=gtime,rtime=rtime)

@app.route("/progress")
def progress():
    tdate = datetime.now().strftime("%d-%m-%Y")
    return redirect(url_for('prog',tdate=tdate))

@app.route("/progress/<tdate>")
def prog(tdate):
    con = sqlite3.connect("static/track.db")
    cur = con.cursor()
    cur.execute("select * from grind where date = ?",(tdate,))
    data = cur.fetchall()
    cur.execute("select tspent from grind where date = ?",(tdate,))
    ts_time = cur.fetchall() #ts_time = total study time
    cur.execute("select rest from grind where date = ?",(tdate,))
    tr_time = cur.fetchall() #tr_time = total rest time
    con.close()
    #getting total study and rest time
    #total study time
    t_s_minutes = f"{sum(int(h[:-1]) * 60 + int(m[:-1]) for h, m in (s[0].split() for s in ts_time))}" 
    hours, minutes = divmod(int(t_s_minutes), 60)
    total_study_time = f"{hours}h {minutes}m"
    #total rest time
    t_r_minutes = f"{sum(int(h[:-1]) * 60 + int(m[:-1]) for h, m in (s[0].split() for s in tr_time))}"
    hours, minutes = divmod(int(t_r_minutes), 60)
    total_rest_time = f"{hours}h {minutes}m"
    #end of getting total study and rest time
    return render_template("progress.html",data=data,ttspent=total_study_time,trest=total_rest_time)
#TRACKER PROGRAM CODE END

if __name__ == "__main__":
    app.run(debug=True,port=80)