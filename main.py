import os
import base64
from flask import Flask, render_template, Response, redirect, request, session, abort, url_for
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from datetime import date
import datetime
import shutil
from random import seed
from random import randint
import mysql.connector
import urllib.request
import urllib.parse
import random
import sys
import time
from flask import send_file

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  charset="utf8",
  database="dna_liquid_stegno"

)

#from store import *


app = Flask(__name__)
app.secret_key = 'abcdef'



@app.route('/', methods=['GET', 'POST'])
def index():
    msg=""
    
    #ff=open("static/dna.txt","r")
    #ddd=ff.read()
    #ff.close()
    #print(ddd)
    
    if request.method=='POST':
        uname=request.form['uname']
        pwd=request.form['pass']
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM register WHERE uname = %s AND pass = %s', (uname, pwd))
        account = cursor.fetchone()
        if account:
            session['username'] = uname
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg=""
    
    #ff=open("static/dna.txt","r")
    #ddd=ff.read()
    #ff.close()
    #print(ddd)
    
    if request.method=='POST':
        uname=request.form['uname']
        pwd=request.form['pass']
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM admin WHERE username = %s AND password = %s', (uname, pwd))
        account = cursor.fetchone()
        if account:
            session['username'] = uname
            return redirect(url_for('admin'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg=""
    mess=""
    email=""
    mycursor = mydb.cursor()
    if request.method=='POST':
        name=request.form['name']
        
        mobile=request.form['mobile']
        
        email=request.form['email']
        uname=request.form['uname']
        pass1=request.form['pass']
        rdate=date.today()
        #print(rdate)

        mess="Dear "+name+", Your Username: "+uname+", Password: "+pass1
        
        mycursor.execute("SELECT max(id)+1 FROM register")
        maxid = mycursor.fetchone()[0]
        if maxid is None:
            maxid=1
        
        now = datetime.datetime.now()
        rdate=now.strftime("%d-%m-%Y")
        cursor = mydb.cursor()
        sql = "INSERT INTO register(id,name,mobile,email,uname,pass) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (maxid,name,mobile,email,uname,pass1)
        cursor.execute(sql, val)
        mydb.commit()            
        print(cursor.rowcount, "Registered Success")
        
        
        if cursor.rowcount==1:
            msg="success"
        else:
            
            msg='fail'  
    return render_template('register.html',msg=msg,email=email,mess=mess)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    msg=""
    act=request.args.get("act")
    mess=""
    email=""
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM register")
    data = mycursor.fetchall()

    if act=="del":
        did=request.args.get("did")
        mycursor.execute("delete from register where id=%s",(did,))
        mydb.commit()
        return redirect(url_for('admin'))            

    return render_template('admin.html',msg=msg,data=data)

@app.route('/home', methods=['GET', 'POST'])
def home():
    msg=""
    data=""
    data2=""
    uid=""
    act = request.args.get('act')
    if act is None:
        act=""
    if 'username' in session:
        uname = session['username']
    #if request.method=='POST':
    #    users=request.form['users']
    #    uu="%"+users+"%"
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM register where uname!=%s",(uname, ))
    data = mycursor.fetchall()
    x=0
    y=0
    for rr in data:
       x+=1
       

    if x==0:
        msg="No Users Found!"
    if act=="ok":
        uid = request.args.get('uid')
        mycursor.execute("SELECT * FROM contacts where (uname=%s and cname=%s) or (uname=%s and cname=%s)",(uname,uid,uid,uname))
        data2 = mycursor.fetchall()
        for rr1 in data2:
            y+=1
        
        if y==0:
            
            mycursor.execute("SELECT max(id)+1 FROM contacts")
            maxid = mycursor.fetchone()[0]
            if maxid is None:
                maxid=1
            cursor = mydb.cursor()
            sql = "INSERT INTO contacts(id,uname,cname,status) VALUES (%s, %s, %s, %s)"
            val = (maxid,uname,uid,'0')
            cursor.execute(sql, val)
            mydb.commit()
            msg="Request Sent"
        else:
            msg="Requst has already sent!" 
    return render_template('home.html',msg=msg,user=uname,data=data)

@app.route('/request1', methods=['GET', 'POST'])
def request1():
    msg=""
    data=""
    data2=""
    uid=""
    c=''
    act = request.args.get('act')
    if act is None:
        act=""
    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM contacts where cname=%s && status=0",(uname, ))
    data = mycursor.fetchall()
    if act=="yes":
        uid = request.args.get('uid')
        j=1
        arr=[]
        while j<=8:
            i=1
            k=''
            while i<=16:
                a1=randint(1, 4)
                if a1==1:
                    c='A'
                elif a1==2:
                    c='C'
                elif a1==3:
                    c='G'
                else:
                    c='T'
                k=k+c
                
                i+=1
            arr.append(k)    
            j+=1
        print(arr[0])
        #print(arr)    
        mycursor.execute("update contacts set status=1,fkey1=%s,rkey1=%s,fkey2=%s,rkey2=%s,fkey3=%s,rkey3=%s,fkey4=%s,rkey4=%s where cname=%s and uname=%s",(arr[0],arr[1],arr[2],arr[3],arr[4],arr[5],arr[6],arr[7],uname,uid))
        mydb.commit()
        msg="Accepted"
    return render_template('request1.html',msg=msg,user=uname,data=data)


@app.route('/cusers', methods=['GET', 'POST'])
def cusers():
    msg=""
    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM contacts where uname=%s or cname=%s",(uname,uname ))
    data = mycursor.fetchall()
    return render_template('cusers.html',msg=msg,user=uname,data=data)

@app.route('/keypair', methods=['GET', 'POST'])
def keypair():
    msg=""
    kid = request.args.get('kid')
    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM contacts where id=%s",(kid, ))
    data = mycursor.fetchone()
    return render_template('keypair.html',user=uname,data=data)

@app.route('/send', methods=['GET', 'POST'])
def send():
    msg=""
    now = datetime.datetime.now()
    rdate=now.strftime("%d-%m-%Y")
    if 'username' in session:
        uname = session['username']
    if request.method=='POST':
        keyid=request.form['keyid']
        sendto=request.form['sendto']
        message=request.form['message']
        cursor = mydb.cursor()

        ff=open("static/dna.txt","w")
        ff.write("")
        ff.close()

        ff2=open("static/dna2.txt","w")
        ff2.write("")
        ff2.close()

        cursor.execute("SELECT * FROM contacts where (uname=%s and cname=%s) or (uname=%s and cname=%s)",(uname,sendto,sendto,uname))
        dr = cursor.fetchone()
        conid=dr[0]

        session['sendto'] = sendto
        
        cursor.execute("SELECT max(id)+1 FROM send_msg")
        maxid = cursor.fetchone()[0]
        if maxid is None:
            maxid=1
        
        sql = "INSERT INTO send_msg(id,uname,cname,kid,message,encmsg,rdate,contactid,value1) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (maxid,uname,sendto,keyid,message,'',rdate,conid,'')
        cursor.execute(sql, val)
        mydb.commit()
        return redirect(url_for('enc_process',mid=str(maxid)))
        
    return render_template('send.html',user=uname)

@app.route('/enc_process', methods=['GET', 'POST'])
def enc_process():
    msg=""
    fkey=""
    mess=""
    email=""
    act = request.args.get('act')
    gf = request.args.get('gf')
    gff=""
    mid = request.args.get('mid')
    if 'username' in session:
        uname = session['username']
    if 'sendto' in session:
        sendto = session['sendto']

    if act is None:
        act="1"
        
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM register where uname=%s",(sendto, ))
    ddd = mycursor.fetchone()
    mobile=ddd[2]
    
    mycursor.execute("SELECT * FROM send_msg where id=%s",(mid, ))
    data = mycursor.fetchone()
    uu=data[2]
    mlen=len(data[4])
    mvalue=mlen*2
    mycursor.execute("SELECT * FROM register where uname=%s",(uu, ))
    ddd2 = mycursor.fetchone()
    email=ddd2[3]

    kid=data[3]
    conid=data[7]
    mycursor.execute("SELECT * FROM contacts where id=%s",(conid, ))
    data2 = mycursor.fetchone()
    if kid==1:
        fkey=data2[4]
    elif kid==2:
        fkey=data2[6]
    elif kid==3:
        fkey=data2[8]
    elif kid==4:
        fkey=data2[10]
        
    
    ##ascii
    dval=''.join(str(ord(c)) for c in data[4])

    ##binary
    line2=''.join(format(ord(x), 'b') for x in data[4])
    bstr2=line2.encode('utf-8')
    dval2=bstr2.decode()

    ##DNA
    hashval=dval2
    #print(hashval)
    #Substitutional Algorithm
    lv=len(hashval)
    gg=""
    i=0
    while i<lv-2:
        g=hashval[i]
        h=hashval[i+1]
        gh=g+""+h
        print(gh)
        if gh=="00":
            gg+="A"
        elif gh=="01":
            gg+="C"
        elif gh=="10":
            gg+="G"
        elif gh=="11":
            gg+="T"
        i+=2
    dval3=gg    
    ##Encrypt
    x1=len(dval3)
    s1="CAGTAGA"
    s2="GCCATCG"
    s3="GTTCAAT"
    s4="CTCAGTG"
    j=0
    kk=""
    while j<x1:
        if dval3[j]=="A":
            kk+="A"+s1
        elif dval3[j]=="C":
            kk+="C"+s2
        elif dval3[j]=="G":
            kk+="G"+s3
        elif dval3[j]=="T":
            kk+="T"+s4
        j+=1
    dval4=kk
    #mvalue=len(dval4)

    mycursor.execute("SELECT * FROM send_msg where id=%s",(mid, ))
    data2 = mycursor.fetchone()

    mycursor.execute("update send_msg set encmsg=%s,value1=%s where id=%s",(dval4,dval,mid))
    mydb.commit()
    
    if request.method=='POST':
        fkey1=request.form['fkey1']
        if fkey==fkey1:
            act="5"
            msg="success"
            mess="New Message received from "+uname+", Message ID:"+str(mid)+", Key ID:"+str(kid)
        else:
            act="4"
            msg="fail"
       
        

        
    return render_template('enc_process.html',user=uname,mid=mid,mvalue=str(mvalue),data=data,dval=dval,dval2=dval2,dval3=dval3,dval4=dval4,fkey=fkey,msg=msg,mess=mess,email=email,act=act)

@app.route('/dna_simulate', methods=['GET', 'POST'])
def dna_simulate():
    msg=""


    return render_template('dna_simulate.html',msg=msg)

@app.route('/received', methods=['GET', 'POST'])
def received():
    msg=""
    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM send_msg where cname=%s order by id desc",(uname, ))
    data = mycursor.fetchall()
    
    return render_template('received.html',user=uname,data=data)


@app.route('/dec_process', methods=['GET', 'POST'])
def dec_process():
    msg=""
    rkey1=""
    rkey=""
    act=request.args.get("act")
    st=""
    data1=""
    data2=""
    data3=""
    data4=""
    data5=""
    emess=""
    mess=""
    mid = request.args.get('mid')
    mycursor = mydb.cursor()
    if 'username' in session:
        uname = session['username']
    ##Recovery Algorithm
    mycursor.execute("SELECT * FROM send_msg where id=%s",(mid, ))
    ddd = mycursor.fetchone()
    kid=ddd[3]
    conid=ddd[7]
    mess=ddd[4]
    emess=ddd[5]
    

    mycursor.execute("SELECT * FROM contacts where id=%s",(conid, ))
    dd1 = mycursor.fetchone()
    if kid==1:
        rkey1=dd1[5]
    elif kid==2:
        rkey1=dd1[7]
    elif kid==3:
        rkey1=dd1[9]
    elif kid==4:
        rkey1=dd1[11]

        
    if request.method=='POST':
        rkey=request.form['rkey']
        if rkey1==rkey:
            act="1"
        else:
            st="1"
            msg="Incorrect Key"
    
    #############
    x1=len(emess)
    j=0
    kk=""
    while j<x1:
        
        kk+=emess[j]
        
        j+=8
    data3=kk
    #############
    lv=len(data3)
    gg=""
    g=""
    i=0
    while i<lv:
        g=data3[i]
        
        
        if g=="A":
            gg+="00"
        elif g=="C":
            gg+="01"
        elif g=="G":
            gg+="10"
        elif g=="T":
            gg+="11"
        i+=1
    data4=gg
    ###################
    line2=''.join(format(ord(x), 'b') for x in data4)
    bstr2=line2.encode('utf-8')
    data5=ddd[8]
        
            
        


        
    return render_template('dec_process.html',user=uname,msg=msg,act=act,mid=mid,data1=emess,data2=mess,data3=data3,data4=data4,data5=data5,st=st)

@app.route('/dna_visual', methods=['GET', 'POST'])
def dna_visual():
    act1=""
    st=""
    dd=[]
    fn=""
    #DNA Strain Generation
    mvalue=request.args.get("mvalue")
    act=request.args.get("act")
    if act is None:
        act="1"
    m=int(mvalue)
    n=int(act)
    data=[]
    PAUSE = 0.15  # Change it 0.0 and see what happen

    #ss=[1,2,3,4]
    ss=[]
    rw=[9,8,7,6,5,4,4,5,6,7,6,6,5,5,6,7,8,9]
    rlen=len(rw)-1

    
    ROWS = [
        '         ##',
        '        #{}-{}#',
        '       #{}---{}#',
        '      #{}-----{}#',
        '     #{}------{}#',
        '    #{}------{}#',
        '    #{}-----{}#',
        '     #{}---{}#',
        '      #{}-{}#',
        '       ##',
        '      #{}-{}#',
        '      #{}---{}#',
        '     #{}-----{}#',
        '     #{}------{}#',
        '      #{}------{}#',
        '       #{}-----{}#',
        '        #{}---{}#',
        '         #{}-{}#',]

    try:
        
        if n<=m:
            st="1"
            print('DNA Visualization || Ihtesham Haider')
            #print('Press CTRL-C on Keyboard to quit....')
            #time.sleep(2)
            rowIndex = 0
            
            s=1
            n+=3
            act1=str(n)
            i=0
            k=0
            spc=[]
            #Main loop of the program || Started
            while i<n:

                dt=[]
                if k<rlen:
                    k+=1
                else:
                    
                    k=0
                nr=rw[k]
                j=1
                spc=[]
                while j<=nr:
                    spc.append('1')
                    
                    j+=1
                
                #incrementing for to draw a next row:
                rowIndex = rowIndex +1
                if rowIndex == len(ROWS):
                    rowIndex = 0

                # Row indexes 0 and 9 don't have nucleotides:
                if rowIndex == 0 or rowIndex ==9:
                    print(ROWS[rowIndex])
                    continue



                randomSelection = random.randint(1,4)
                if randomSelection ==1:
                    leftNucleotide, rightNucleotide = 'A', 'T'
                elif randomSelection ==2:
                    leftNucleotide, rightNucleotide = 'T', 'A'
                elif randomSelection ==3:
                    leftNucleotide, rightNucleotide = 'C', 'G'
                elif randomSelection ==4:
                    leftNucleotide, rightNucleotide = 'G', 'C'

                # priting the row
                #print(ROWS[rowIndex].format(leftNucleotide, rightNucleotide))
                dd=ROWS[rowIndex].format(leftNucleotide, rightNucleotide)

                
                ff=open("static/dna.txt","a")
                
                ff.write("\n"+dd)
                ff.close()


                ff2=open("static/dna2.txt","a")
                ff2.write(dd+"|")
                ff2.close()
                
                dt.append(spc)
                dt.append(dd)
                data.append(dt)
                
                i+=1
            
            #fasta
            #shutil.copy("static/dna.txt","static/dna.fa")
            
        else:
            ff=open("static/dna2.txt","r")
            ddd=ff.read()
            ff.close()
            arr1=ddd.split("|")
            
            alen=len(arr1)
            ########################
            #File input
            fileInput = open("static/dna.txt", "r")

            #File output
            fn="dna.fasta"
            fileOutput = open("static/"+fn, "w")

            #Seq count
            count = 1 

            #Loop through each line in the input file
            print("Converting to FASTA...")
            for strLine in fileInput:

                #Strip the endline character from each input line
                strLine = strLine.rstrip("\n")

                #Output the header
                fileOutput.write(">" + str(count) + "\n")
                fileOutput.write(strLine + "\n")

                count = count + 1
            print ("Done.")

            #Close the input and output file
            fileInput.close()
            fileOutput.close()
            #######################
            k=0
            i=0
            dat=[]
            x=0
            '''with open('static/dna.txt') as f:
                dline=f.readlines()
                gs=str(dline)
                dline1=gs.rstrip('\n')
                dat.append(gs)
                x+=1'''
               

            for dat1 in arr1:
                if i<alen:
                    
                    print("k=")
                    print(k)
                    nr=rw[k]

                    if k<rlen-1:
                        k+=1
                    else:
                        k=0
                    j=1
                    spc1=[]
                    while j<=nr:
                        spc1.append('1')
                        
                        j+=1

                        
                    df=[]
                    df.append(spc1)
                    
                    dg = dat1.strip()
                    
                    df.append(dg)
                    dd.append(df)

                
                
                i+=1
                
    
            st="2"
    except KeyboardInterrupt:
        sys.exit()

        
        

    return render_template('dna_visual.html',ss=ss,data=data,act=act1,st=st,dd=dd,mvalue=mvalue,fn=fn)

@app.route('/down', methods=['GET', 'POST'])
def down():
    fn = request.args.get('fname')
    path="static/"+fn
    return send_file(path, as_attachment=True)


@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
