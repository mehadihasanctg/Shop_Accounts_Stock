from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime
import os, shutil

BASE=os.path.abspath(os.path.dirname(__file__)); INSTANCE=os.path.join(BASE,'instance'); os.makedirs(INSTANCE,exist_ok=True)
app=Flask(__name__); app.secret_key='shop-accounts-change-me'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(INSTANCE,'shop_accounts.db'); app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)

class Setting(db.Model): id=db.Column(db.Integer,primary_key=True); key=db.Column(db.String(80),unique=True); value=db.Column(db.String(255))
class User(db.Model): id=db.Column(db.Integer,primary_key=True); username=db.Column(db.String(80),unique=True); password_hash=db.Column(db.String(255)); role=db.Column(db.String(20),default='user'); active=db.Column(db.Boolean,default=True)
class Showroom(db.Model): id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(120),unique=True); address=db.Column(db.String(255)); manager=db.Column(db.String(120)); contact=db.Column(db.String(50)); active=db.Column(db.Boolean,default=True)
class Category(db.Model): id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(120),unique=True); active=db.Column(db.Boolean,default=True)
class Product(db.Model): id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(150)); category_id=db.Column(db.Integer,db.ForeignKey('category.id')); barcode=db.Column(db.String(100),unique=True); sku=db.Column(db.String(80)); sale_price=db.Column(db.Float,default=0); purchase_price=db.Column(db.Float,default=0); reorder_level=db.Column(db.Integer,default=1); active=db.Column(db.Boolean,default=True); category=db.relationship('Category')
class Customer(db.Model): id=db.Column(db.Integer,primary_key=True); customer_code=db.Column(db.String(30),unique=True); name=db.Column(db.String(150)); mobile=db.Column(db.String(50)); address=db.Column(db.String(255)); reference_name=db.Column(db.String(120)); reference_number=db.Column(db.String(50)); showroom_id=db.Column(db.Integer,db.ForeignKey('showroom.id')); opening_due=db.Column(db.Float,default=0); opening_advance=db.Column(db.Float,default=0); active=db.Column(db.Boolean,default=True); showroom=db.relationship('Showroom')
class Supplier(db.Model): id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(150)); mobile=db.Column(db.String(50)); address=db.Column(db.String(255)); opening_due=db.Column(db.Float,default=0); opening_advance=db.Column(db.Float,default=0); active=db.Column(db.Boolean,default=True)
class Stock(db.Model): id=db.Column(db.Integer,primary_key=True); product_id=db.Column(db.Integer,db.ForeignKey('product.id')); showroom_id=db.Column(db.Integer,db.ForeignKey('showroom.id')); qty=db.Column(db.Integer,default=0); product=db.relationship('Product'); showroom=db.relationship('Showroom')
class BankAccount(db.Model): id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(150)); bank_name=db.Column(db.String(150)); branch=db.Column(db.String(150)); account_no=db.Column(db.String(100)); routing_no=db.Column(db.String(100)); account_type=db.Column(db.String(50)); opening_balance=db.Column(db.Float,default=0); active=db.Column(db.Boolean,default=True)
class Investor(db.Model): id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(150)); mobile=db.Column(db.String(50)); designation=db.Column(db.String(100)); active=db.Column(db.Boolean,default=True)
class Sale(db.Model):
 id=db.Column(db.Integer,primary_key=True); invoice=db.Column(db.String(40)); dt=db.Column(db.Date,default=date.today); showroom_id=db.Column(db.Integer); customer_id=db.Column(db.Integer); product_id=db.Column(db.Integer); qty=db.Column(db.Integer); unit_price=db.Column(db.Float); gross=db.Column(db.Float); discount=db.Column(db.Float); net=db.Column(db.Float); payment_type=db.Column(db.String(30)); bank_account_id=db.Column(db.Integer); first_payment=db.Column(db.Float,default=0); installment_due=db.Column(db.Float,default=0); installment_months=db.Column(db.Integer,default=0); installment_start=db.Column(db.Date); guarantee_cheque_no=db.Column(db.String(80)); guarantee_bank=db.Column(db.String(120)); guarantee_branch=db.Column(db.String(120)); guarantee_date=db.Column(db.Date); guarantee_amount=db.Column(db.Float,default=0); notes=db.Column(db.String(255))
class Purchase(db.Model): id=db.Column(db.Integer,primary_key=True); invoice=db.Column(db.String(40)); dt=db.Column(db.Date,default=date.today); showroom_id=db.Column(db.Integer); supplier_id=db.Column(db.Integer); product_id=db.Column(db.Integer); qty=db.Column(db.Integer); unit_price=db.Column(db.Float); total=db.Column(db.Float); payment_type=db.Column(db.String(30)); bank_account_id=db.Column(db.Integer); notes=db.Column(db.String(255))
class ExpenseHead(db.Model): id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(120),unique=True); expense_type=db.Column(db.String(30),default='Direct'); active=db.Column(db.Boolean,default=True)
class Expense(db.Model): id=db.Column(db.Integer,primary_key=True); dt=db.Column(db.Date,default=date.today); showroom_id=db.Column(db.Integer); head_id=db.Column(db.Integer,db.ForeignKey('expense_head.id')); category=db.Column(db.String(120)); amount=db.Column(db.Float); payment_method=db.Column(db.String(30)); bank_account_id=db.Column(db.Integer); notes=db.Column(db.String(255)); head=db.relationship('ExpenseHead')
class Investment(db.Model): id=db.Column(db.Integer,primary_key=True); dt=db.Column(db.Date,default=date.today); showroom_id=db.Column(db.Integer); investor_id=db.Column(db.Integer); amount=db.Column(db.Float); method=db.Column(db.String(30)); bank_account_id=db.Column(db.Integer); description=db.Column(db.String(255))
class Asset(db.Model): id=db.Column(db.Integer,primary_key=True); dt=db.Column(db.Date,default=date.today); showroom_id=db.Column(db.Integer); name=db.Column(db.String(150)); value=db.Column(db.Float); notes=db.Column(db.String(255)); active=db.Column(db.Boolean,default=True)
class Liability(db.Model): id=db.Column(db.Integer,primary_key=True); dt=db.Column(db.Date,default=date.today); showroom_id=db.Column(db.Integer); name=db.Column(db.String(150)); amount=db.Column(db.Float); notes=db.Column(db.String(255)); active=db.Column(db.Boolean,default=True)
class Loan(db.Model): id=db.Column(db.Integer,primary_key=True); dt=db.Column(db.Date,default=date.today); showroom_id=db.Column(db.Integer); party_type=db.Column(db.String(30)); party_id=db.Column(db.Integer); party_name=db.Column(db.String(150)); principal=db.Column(db.Float); paid=db.Column(db.Float,default=0); interest=db.Column(db.Float,default=0); due_date=db.Column(db.Date); direction=db.Column(db.String(20)); notes=db.Column(db.String(255)); active=db.Column(db.Boolean,default=True)
class Advance(db.Model): id=db.Column(db.Integer,primary_key=True); dt=db.Column(db.Date,default=date.today); showroom_id=db.Column(db.Integer); customer_id=db.Column(db.Integer); supplier_id=db.Column(db.Integer); amount=db.Column(db.Float); adjusted=db.Column(db.Float,default=0); direction=db.Column(db.String(30)); method=db.Column(db.String(30)); bank_account_id=db.Column(db.Integer); notes=db.Column(db.String(255))
class OpeningBalance(db.Model): id=db.Column(db.Integer,primary_key=True); dt=db.Column(db.Date,default=date.today); showroom_id=db.Column(db.Integer); account_type=db.Column(db.String(50)); account_name=db.Column(db.String(150)); amount=db.Column(db.Float); direction=db.Column(db.String(20)); notes=db.Column(db.String(255))
class OpeningStock(db.Model): id=db.Column(db.Integer,primary_key=True); dt=db.Column(db.Date,default=date.today); showroom_id=db.Column(db.Integer,db.ForeignKey('showroom.id')); product_id=db.Column(db.Integer,db.ForeignKey('product.id')); qty=db.Column(db.Integer); unit_cost=db.Column(db.Float); notes=db.Column(db.String(255)); showroom=db.relationship('Showroom'); product=db.relationship('Product')
class CashEntry(db.Model): id=db.Column(db.Integer,primary_key=True); dt=db.Column(db.Date,default=date.today); showroom_id=db.Column(db.Integer); entry_type=db.Column(db.String(20)); category=db.Column(db.String(120)); party=db.Column(db.String(150)); amount=db.Column(db.Float); reference=db.Column(db.String(100)); notes=db.Column(db.String(255))
class BankEntry(db.Model): id=db.Column(db.Integer,primary_key=True); dt=db.Column(db.Date,default=date.today); showroom_id=db.Column(db.Integer); bank_account_id=db.Column(db.Integer); entry_type=db.Column(db.String(20)); category=db.Column(db.String(120)); party=db.Column(db.String(150)); amount=db.Column(db.Float); reference=db.Column(db.String(100)); notes=db.Column(db.String(255))
class Installment(db.Model): id=db.Column(db.Integer,primary_key=True); sale_id=db.Column(db.Integer); customer_id=db.Column(db.Integer); due_date=db.Column(db.Date); amount=db.Column(db.Float); paid=db.Column(db.Float,default=0); status=db.Column(db.String(20),default='Due')
class Audit(db.Model): id=db.Column(db.Integer,primary_key=True); dt=db.Column(db.DateTime,default=datetime.now); username=db.Column(db.String(80)); action=db.Column(db.String(50)); module=db.Column(db.String(80)); details=db.Column(db.String(500))
class InstallmentPayment(db.Model): id=db.Column(db.Integer,primary_key=True); installment_id=db.Column(db.Integer); dt=db.Column(db.Date,default=date.today); amount=db.Column(db.Float); method=db.Column(db.String(30)); bank_account_id=db.Column(db.Integer); reference=db.Column(db.String(100)); notes=db.Column(db.String(255))

def S(k,d=''): x=Setting.query.filter_by(key=k).first(); return x.value if x else d
def admin(): return session.get('role')=='admin'
def require_admin():
 if not admin(): abort(403)
def stock_for(pid,sid):
 s=Stock.query.filter_by(product_id=pid,showroom_id=sid).first()
 if not s: s=Stock(product_id=pid,showroom_id=sid,qty=0); db.session.add(s); db.session.flush()
 return s
def audit(action,module,details): db.session.add(Audit(username=session.get('username','system'),action=action,module=module,details=details)); db.session.commit()
@app.before_request
def init():
 db.create_all()
 if not User.query.filter_by(username='admin').first(): db.session.add(User(username='admin',password_hash=generate_password_hash('Admin@123'),role='admin'))
 if not User.query.filter_by(username='user').first(): db.session.add(User(username='user',password_hash=generate_password_hash('User@123'),role='user'))
 if not Setting.query.filter_by(key='shop_name').first(): db.session.add(Setting(key='shop_name',value='SHOP NAME'))
 if not Setting.query.filter_by(key='owner').first(): db.session.add(Setting(key='owner',value='Mr. Taher'))
 db.session.commit()
@app.context_processor
def ctx(): return dict(shop_name=S('shop_name','SHOP NAME'),owner=S('owner','Mr. Taher'),today=date.today(),logged_in='user_id' in session,role=session.get('role'))
@app.route('/login',methods=['GET','POST'])
def login():
 if request.method=='POST':
  u=User.query.filter_by(username=request.form['username'],active=True).first()
  if u and check_password_hash(u.password_hash,request.form['password']): session.update(user_id=u.id,username=u.username,role=u.role); return redirect(url_for('dashboard'))
  flash('Invalid username or password','danger')
 return render_template('login.html')
@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))
@app.before_request
def auth():
 if request.endpoint not in ('login','static') and 'user_id' not in session: return redirect(url_for('login'))
@app.route('/')
def dashboard():
 return render_template('dashboard.html',sales=sum(x.net or 0 for x in Sale.query.filter_by(dt=date.today())),purchases=sum(x.total or 0 for x in Purchase.query.filter_by(dt=date.today())),expenses=sum(x.amount or 0 for x in Expense.query.filter_by(dt=date.today())))
@app.route('/settings',methods=['GET','POST'])
def settings():
 require_admin()
 if request.method=='POST':
  for k in ('shop_name','owner'):
   x=Setting.query.filter_by(key=k).first() or Setting(key=k); x.value=request.form.get(k,''); db.session.add(x)
  db.session.commit(); flash('Settings saved','success')
 return render_template('settings.html')

def master_route(model,title,fields,template='master.html'):
 rows=model.query.order_by(model.id.desc()).all(); return render_template(template,title=title,rows=rows,fields=fields)
@app.route('/showrooms',methods=['GET','POST'])
def showrooms():
 require_admin()
 if request.method=='POST': db.session.add(Showroom(name=request.form['name'],address=request.form.get('address',''),manager=request.form.get('manager',''),contact=request.form.get('contact',''))); db.session.commit(); return redirect(url_for('showrooms'))
 return render_template('showrooms.html',rows=Showroom.query.order_by(Showroom.id.desc()).all())
@app.route('/categories',methods=['GET','POST'])
def categories():
 require_admin()
 if request.method=='POST': db.session.add(Category(name=request.form['name'])); db.session.commit(); return redirect(url_for('categories'))
 return render_template('categories.html',rows=Category.query.order_by(Category.id.desc()).all())
@app.route('/products',methods=['GET','POST'])
def products():
 require_admin()
 if request.method=='POST': db.session.add(Product(name=request.form['name'],category_id=int(request.form['category_id']),barcode=request.form.get('barcode','') or None,sku=request.form.get('sku',''),sale_price=float(request.form.get('sale_price') or 0),purchase_price=float(request.form.get('purchase_price') or 0),reorder_level=int(request.form.get('reorder_level') or 1))); db.session.commit(); return redirect(url_for('products'))
 return render_template('products.html',rows=Product.query.order_by(Product.id.desc()).all(),cats=Category.query.filter_by(active=True).all())
@app.route('/customers',methods=['GET','POST'])
def customers():
 if request.method=='POST':
  code='C'+datetime.now().strftime('%y%m%d%H%M%S%f')[-10:]; db.session.add(Customer(customer_code=code,name=request.form['name'],mobile=request.form.get('mobile',''),address=request.form.get('address',''),reference_name=request.form.get('reference_name',''),reference_number=request.form.get('reference_number',''),showroom_id=int(request.form['showroom_id']),opening_due=float(request.form.get('opening_due') or 0),opening_advance=float(request.form.get('opening_advance') or 0))); db.session.commit(); return redirect(url_for('customers'))
 return render_template('customers.html',rows=Customer.query.order_by(Customer.id.desc()).all(),showrooms=Showroom.query.filter_by(active=True).all())
@app.route('/suppliers',methods=['GET','POST'])
def suppliers():
 if request.method=='POST': db.session.add(Supplier(name=request.form['name'],mobile=request.form.get('mobile',''),address=request.form.get('address',''),opening_due=float(request.form.get('opening_due') or 0),opening_advance=float(request.form.get('opening_advance') or 0))); db.session.commit(); return redirect(url_for('suppliers'))
 return render_template('suppliers.html',rows=Supplier.query.order_by(Supplier.id.desc()).all())
@app.route('/investors',methods=['GET','POST'])
def investors():
 require_admin()
 if request.method=='POST': db.session.add(Investor(name=request.form['name'],mobile=request.form.get('mobile',''),designation=request.form.get('designation',''))); db.session.commit(); return redirect(url_for('investors'))
 return render_template('investors.html',rows=Investor.query.order_by(Investor.id.desc()).all())
@app.route('/bank-accounts',methods=['GET','POST'])
def bank_accounts():
 require_admin()
 if request.method=='POST': db.session.add(BankAccount(name=request.form['name'],bank_name=request.form.get('bank_name',''),branch=request.form.get('branch',''),account_no=request.form.get('account_no',''),routing_no=request.form.get('routing_no',''),account_type=request.form.get('account_type',''),opening_balance=float(request.form.get('opening_balance') or 0))); db.session.commit(); return redirect(url_for('bank_accounts'))
 return render_template('bank_accounts.html',rows=BankAccount.query.order_by(BankAccount.id.desc()).all())
@app.route('/sales',methods=['GET','POST'])
def sales():
 if request.method=='POST':
  sid=int(request.form['showroom_id']); pid=int(request.form['product_id']); qty=int(request.form['qty']); st=stock_for(pid,sid)
  if st.qty<qty: flash(f'Not enough stock. Available {st.qty}','danger'); return redirect(url_for('sales'))
  gross=qty*float(request.form['unit_price']); disc=float(request.form.get('discount') or 0); net=max(0,gross-disc); pay=request.form['payment_type']; first=float(request.form.get('first_payment') or 0); due=max(0,net-first) if pay=='Installment' else (net if pay=='Due' else 0)
  bank_id=int(request.form.get('bank_account_id') or 0) or None
  s=Sale(invoice=request.form.get('invoice') or 'S-'+datetime.now().strftime('%Y%m%d%H%M%S'),dt=datetime.strptime(request.form['dt'],'%Y-%m-%d').date(),showroom_id=sid,customer_id=int(request.form.get('customer_id') or 0) or None,product_id=pid,qty=qty,unit_price=float(request.form['unit_price']),gross=gross,discount=disc,net=net,payment_type=pay,bank_account_id=bank_id,first_payment=first,installment_due=due,installment_months=int(request.form.get('installment_months') or 0),installment_start=datetime.strptime(request.form['installment_start'],'%Y-%m-%d').date() if request.form.get('installment_start') else None,guarantee_cheque_no=request.form.get('guarantee_cheque_no',''),guarantee_bank=request.form.get('guarantee_bank',''),guarantee_branch=request.form.get('guarantee_branch',''),guarantee_date=datetime.strptime(request.form['guarantee_date'],'%Y-%m-%d').date() if request.form.get('guarantee_date') else None,guarantee_amount=float(request.form.get('guarantee_amount') or 0),notes=request.form.get('notes',''))
  db.session.add(s); st.qty-=qty; db.session.commit()
  if pay=='Installment' and s.installment_months and due:
   from dateutil.relativedelta import relativedelta
   monthly=due/s.installment_months; start=s.installment_start or s.dt
   for i in range(s.installment_months): db.session.add(Installment(sale_id=s.id,customer_id=s.customer_id,due_date=start+relativedelta(months=i),amount=monthly))
   db.session.commit()
  if pay in ('Cash','Installment') and first: db.session.add(CashEntry(dt=s.dt,showroom_id=sid,entry_type='Receipt',category='Sale',party=str(s.customer_id or ''),amount=first,reference=s.invoice)); db.session.commit()
  if pay=='Bank': db.session.add(BankEntry(dt=s.dt,showroom_id=sid,bank_account_id=bank_id,entry_type='Receipt',category='Sale',party=str(s.customer_id or ''),amount=net,reference=s.invoice)); db.session.commit()
  audit('CREATE','SALE',s.invoice); flash('Sale saved; stock reduced','success'); return redirect(url_for('sales'))
 return render_template('sales.html',rows=Sale.query.order_by(Sale.id.desc()).limit(100).all(),showrooms=Showroom.query.filter_by(active=True).all(),products=Product.query.filter_by(active=True).all(),customers=Customer.query.filter_by(active=True).all(),banks=BankAccount.query.filter_by(active=True).all(),installments=Installment.query.filter(Installment.status!='Paid').order_by(Installment.due_date).limit(20).all())
@app.route('/purchases',methods=['GET','POST'])
def purchases():
 if request.method=='POST':
  sid=int(request.form['showroom_id']); pid=int(request.form['product_id']); qty=int(request.form['qty']); total=qty*float(request.form['unit_price']); bank_id=int(request.form.get('bank_account_id') or 0) or None
  p=Purchase(invoice=request.form.get('invoice') or 'P-'+datetime.now().strftime('%Y%m%d%H%M%S'),dt=datetime.strptime(request.form['dt'],'%Y-%m-%d').date(),showroom_id=sid,supplier_id=int(request.form.get('supplier_id') or 0) or None,product_id=pid,qty=qty,unit_price=float(request.form['unit_price']),total=total,payment_type=request.form['payment_type'],bank_account_id=bank_id,notes=request.form.get('notes','')); db.session.add(p); stock_for(pid,sid).qty+=qty; db.session.commit(); audit('CREATE','PURCHASE',p.invoice); return redirect(url_for('purchases'))
 return render_template('purchases.html',rows=Purchase.query.order_by(Purchase.id.desc()).limit(100).all(),showrooms=Showroom.query.filter_by(active=True).all(),categories=Category.query.filter_by(active=True).all(),products=Product.query.filter_by(active=True).all(),suppliers=Supplier.query.filter_by(active=True).all(),banks=BankAccount.query.filter_by(active=True).all())
@app.route('/opening-stock',methods=['GET','POST'])
def opening_stock():
 if request.method=='POST':
  sid=int(request.form['showroom_id']); pid=int(request.form['product_id']); qty=int(request.form['qty']); cost=float(request.form['unit_cost']); db.session.add(OpeningStock(dt=datetime.strptime(request.form['dt'],'%Y-%m-%d').date(),showroom_id=sid,product_id=pid,qty=qty,unit_cost=cost,notes=request.form.get('notes',''))); stock_for(pid,sid).qty+=qty; db.session.commit(); audit('CREATE','OPENING STOCK',f'{pid}/{sid}/{qty}'); return redirect(url_for('opening_stock'))
 return render_template('opening_stock.html',rows=OpeningStock.query.order_by(OpeningStock.id.desc()).all(),showrooms=Showroom.query.filter_by(active=True).all(),categories=Category.query.filter_by(active=True).all())
@app.route('/expense-heads',methods=['GET','POST'])
def expense_heads():
 require_admin()
 if request.method=='POST': db.session.add(ExpenseHead(name=request.form['name'],expense_type=request.form.get('expense_type','Direct'))); db.session.commit(); return redirect(url_for('expense_heads'))
 return render_template('expense_heads.html',rows=ExpenseHead.query.order_by(ExpenseHead.name).all())
@app.route('/expenses',methods=['GET','POST'])
def expenses():
 if request.method=='POST':
  h=ExpenseHead.query.get(int(request.form['head_id']))
  db.session.add(Expense(dt=datetime.strptime(request.form['dt'],'%Y-%m-%d').date(),showroom_id=int(request.form['showroom_id']),head_id=h.id,category=h.name,amount=float(request.form['amount']),payment_method=request.form['payment_method'],bank_account_id=int(request.form.get('bank_account_id') or 0) or None,notes=request.form.get('notes',''))); db.session.commit(); return redirect(url_for('expenses'))
 return render_template('expenses.html',rows=Expense.query.order_by(Expense.id.desc()).all(),showrooms=Showroom.query.filter_by(active=True).all(),banks=BankAccount.query.filter_by(active=True).all(),heads=ExpenseHead.query.filter_by(active=True).order_by(ExpenseHead.expense_type,ExpenseHead.name).all())
@app.route('/investments',methods=['GET','POST'])
def investments():
 if request.method=='POST': db.session.add(Investment(dt=datetime.strptime(request.form['dt'],'%Y-%m-%d').date(),showroom_id=int(request.form['showroom_id']),investor_id=int(request.form['investor_id']),amount=float(request.form['amount']),method=request.form['method'],bank_account_id=int(request.form.get('bank_account_id') or 0) or None,description=request.form.get('description',''))); db.session.commit(); return redirect(url_for('investments'))
 return render_template('investments.html',rows=Investment.query.order_by(Investment.id.desc()).all(),showrooms=Showroom.query.filter_by(active=True).all(),investors=Investor.query.filter_by(active=True).all(),banks=BankAccount.query.filter_by(active=True).all())
@app.route('/assets',methods=['GET','POST'])
def assets():
 require_admin()
 if request.method=='POST': db.session.add(Asset(dt=datetime.strptime(request.form['dt'],'%Y-%m-%d').date(),showroom_id=int(request.form['showroom_id']),name=request.form['name'],value=float(request.form['value']),notes=request.form.get('notes',''))); db.session.commit(); return redirect(url_for('assets'))
 return render_template('finance.html',title='Assets',rows=Asset.query.order_by(Asset.id.desc()).all(),showrooms=Showroom.query.all(),kind='asset')
@app.route('/liabilities',methods=['GET','POST'])
def liabilities():
 require_admin()
 if request.method=='POST': db.session.add(Liability(dt=datetime.strptime(request.form['dt'],'%Y-%m-%d').date(),showroom_id=int(request.form['showroom_id']),name=request.form['name'],amount=float(request.form['amount']),notes=request.form.get('notes',''))); db.session.commit(); return redirect(url_for('liabilities'))
 return render_template('finance.html',title='Liabilities',rows=Liability.query.order_by(Liability.id.desc()).all(),showrooms=Showroom.query.all(),kind='liability')
@app.route('/loans',methods=['GET','POST'])
def loans():
 if request.method=='POST': db.session.add(Loan(dt=datetime.strptime(request.form['dt'],'%Y-%m-%d').date(),showroom_id=int(request.form['showroom_id']),party_type=request.form['party_type'],party_id=int(request.form.get('party_id') or 0) or None,party_name=request.form.get('party_name',''),principal=float(request.form['principal']),interest=float(request.form.get('interest') or 0),due_date=datetime.strptime(request.form['due_date'],'%Y-%m-%d').date() if request.form.get('due_date') else None,direction=request.form['direction'],notes=request.form.get('notes',''))); db.session.commit(); return redirect(url_for('loans'))
 return render_template('loans.html',rows=Loan.query.order_by(Loan.id.desc()).all(),showrooms=Showroom.query.filter_by(active=True).all(),suppliers=Supplier.query.filter_by(active=True).all(),banks=BankAccount.query.filter_by(active=True).all())
@app.route('/advances',methods=['GET','POST'])
def advances():
 if request.method=='POST': db.session.add(Advance(dt=datetime.strptime(request.form['dt'],'%Y-%m-%d').date(),showroom_id=int(request.form['showroom_id']),customer_id=int(request.form.get('customer_id') or 0) or None,supplier_id=int(request.form.get('supplier_id') or 0) or None,amount=float(request.form['amount']),direction=request.form['direction'],method=request.form['method'],bank_account_id=int(request.form.get('bank_account_id') or 0) or None,notes=request.form.get('notes',''))); db.session.commit(); return redirect(url_for('advances'))
 return render_template('advances.html',rows=Advance.query.order_by(Advance.id.desc()).all(),showrooms=Showroom.query.all(),customers=Customer.query.filter_by(active=True).all(),suppliers=Supplier.query.filter_by(active=True).all(),banks=BankAccount.query.filter_by(active=True).all())
@app.route('/cash-book',methods=['GET','POST'])
def cash_book():
 if request.method=='POST': db.session.add(CashEntry(dt=datetime.strptime(request.form['dt'],'%Y-%m-%d').date(),showroom_id=int(request.form['showroom_id']),entry_type=request.form['entry_type'],category=request.form['category'],party=request.form.get('party',''),amount=float(request.form['amount']),reference=request.form.get('reference',''),notes=request.form.get('notes',''))); db.session.commit(); return redirect(url_for('cash_book'))
 return render_template('cash_book.html',rows=CashEntry.query.order_by(CashEntry.dt.desc(),CashEntry.id.desc()).all(),showrooms=Showroom.query.filter_by(active=True).all())
@app.route('/bank-book',methods=['GET','POST'])
def bank_book():
 if request.method=='POST': db.session.add(BankEntry(dt=datetime.strptime(request.form['dt'],'%Y-%m-%d').date(),showroom_id=int(request.form['showroom_id']),bank_account_id=int(request.form['bank_account_id']),entry_type=request.form['entry_type'],category=request.form['category'],party=request.form.get('party',''),amount=float(request.form['amount']),reference=request.form.get('reference',''),notes=request.form.get('notes',''))); db.session.commit(); return redirect(url_for('bank_book'))
 return render_template('bank_book.html',rows=BankEntry.query.order_by(BankEntry.dt.desc(),BankEntry.id.desc()).all(),showrooms=Showroom.query.filter_by(active=True).all(),banks=BankAccount.query.filter_by(active=True).all())
@app.route('/opening',methods=['GET','POST'])
def opening():
 if request.method=='POST': db.session.add(OpeningBalance(dt=datetime.strptime(request.form['dt'],'%Y-%m-%d').date(),showroom_id=int(request.form['showroom_id']),account_type=request.form['account_type'],account_name=request.form['account_name'],amount=float(request.form['amount']),direction=request.form['direction'],notes=request.form.get('notes',''))); db.session.commit(); return redirect(url_for('opening'))
 return render_template('opening.html',rows=OpeningBalance.query.order_by(OpeningBalance.id.desc()).all(),showrooms=Showroom.query.filter_by(active=True).all())
@app.route('/stock')
def stock():
 category_id=request.args.get('category_id',type=int)
 showroom_id=request.args.get('showroom_id',type=int)
 sort=request.args.get('sort','product')
 q=Stock.query
 if showroom_id: q=q.filter(Stock.showroom_id==showroom_id)
 rows=q.join(Product).join(Category).all()
 if category_id: rows=[r for r in rows if r.product.category_id==category_id]
 data=[]
 for r in rows:
  value=(r.qty or 0)*(r.product.purchase_price or 0)
  data.append({'row':r,'value':value})
 if sort=='category': data.sort(key=lambda z:(z['row'].product.category.name.lower(),z['row'].product.name.lower()))
 elif sort=='value_desc': data.sort(key=lambda z:z['value'],reverse=True)
 elif sort=='value_asc': data.sort(key=lambda z:z['value'])
 elif sort=='showroom': data.sort(key=lambda z:(z['row'].showroom.name.lower(),z['row'].product.name.lower()))
 else: data.sort(key=lambda z:z['row'].product.name.lower())
 total_value=sum(z['value'] for z in data); total_qty=sum(z['row'].qty or 0 for z in data)
 return render_template('stock.html',rows=data,showrooms=Showroom.query.filter_by(active=True).order_by(Showroom.name).all(),categories=Category.query.filter_by(active=True).order_by(Category.name).all(),category_id=category_id,showroom_id=showroom_id,sort=sort,total_value=total_value,total_qty=total_qty)
@app.route('/installment/<int:id>/collect',methods=['GET','POST'])
def collect_installment(id):
 inst=Installment.query.get_or_404(id); sale=Sale.query.get(inst.sale_id); banks=BankAccount.query.filter_by(active=True).order_by(BankAccount.name).all()
 if request.method=='POST':
  amount=float(request.form['amount']); remaining=max(0,(inst.amount or 0)-(inst.paid or 0))
  if amount<=0 or amount>remaining: flash('Invalid collection amount','danger'); return redirect(url_for('installments'))
  db.session.add(InstallmentPayment(installment_id=id,dt=datetime.strptime(request.form['dt'],'%Y-%m-%d').date(),amount=amount,method=request.form['method'],bank_account_id=int(request.form.get('bank_account_id') or 0) or None,reference=request.form.get('reference',''),notes=request.form.get('notes','')))
  inst.paid=(inst.paid or 0)+amount; inst.status='Paid' if inst.paid>=inst.amount else 'Partial'; db.session.commit(); audit('CREATE','INSTALLMENT COLLECTION',str(id)); flash('Installment payment recorded','success'); return redirect(url_for('installments'))
 return render_template('collect_installment.html',inst=inst,sale=sale,banks=banks)

@app.route('/installments')
def installments(): return render_template('installments.html',rows=Installment.query.order_by(Installment.due_date).all())
@app.route('/ledger')
def ledger():
 module=request.args.get('module','all')
 showroom_id=request.args.get('showroom_id',type=int)
 party=request.args.get('party','').strip().lower()
 rows=[]
 def add(dt,mod,ref,party_name,amount,typ,showroom=''):
  if module!='all' and module.lower()!=mod.lower(): return
  if showroom_id and showroom_id != getattr(showroom,'id',None): return
  if party and party not in str(party_name or '').lower(): return
  rows.append((dt,mod,ref,party_name,amount,typ,showroom))
 for x in Sale.query.all(): add(x.dt,'Sales',x.invoice,str(x.customer_id or ''),x.net,'Receipt/Due',Showroom.query.get(x.showroom_id))
 for x in Purchase.query.all(): add(x.dt,'Purchase',x.invoice,str(x.supplier_id or ''),x.total,'Purchase',Showroom.query.get(x.showroom_id))
 for x in Expense.query.all(): add(x.dt,'Expense',x.category,x.category,x.amount,'Payment',Showroom.query.get(x.showroom_id))
 for x in Investment.query.all(): add(x.dt,'Investment',str(x.id),str(x.investor_id),x.amount,'Capital',Showroom.query.get(x.showroom_id))
 for x in Loan.query.all(): add(x.dt,'Loan',str(x.id),x.party_name,x.principal,x.direction,Showroom.query.get(x.showroom_id))
 for x in Advance.query.all(): add(x.dt,'Advance',str(x.id),str(x.customer_id or x.supplier_id or ''),x.amount,x.direction,Showroom.query.get(x.showroom_id))
 for x in CashEntry.query.all(): add(x.dt,'Cash',x.reference,x.party,x.amount,x.entry_type,Showroom.query.get(x.showroom_id))
 for x in BankEntry.query.all(): add(x.dt,'Bank',x.reference,x.party,x.amount,x.entry_type,Showroom.query.get(x.showroom_id))
 for x in Asset.query.all(): add(x.dt,'Asset',str(x.id),x.name,x.value,'Asset',Showroom.query.get(x.showroom_id))
 for x in Liability.query.all(): add(x.dt,'Liability',str(x.id),x.name,x.amount,'Liability',Showroom.query.get(x.showroom_id))
 return render_template('ledger.html',rows=sorted(rows,key=lambda z:z[0],reverse=True),module=module,showrooms=Showroom.query.filter_by(active=True).order_by(Showroom.name).all(),showroom_id=showroom_id,party=request.args.get('party',''))

@app.route('/entity-ledger/<entity>/<int:id>')
def entity_ledger(entity,id):
 rows=[]; title='Ledger'
 if entity=='customer':
  obj=Customer.query.get_or_404(id); title='Customer Ledger — '+obj.name
  for x in Sale.query.filter_by(customer_id=id).all(): rows.append((x.dt,'Sales',x.invoice,x.net,'Debit'))
  for x in Advance.query.filter_by(customer_id=id).all(): rows.append((x.dt,'Advance',str(x.id),x.amount,'Credit' if x.direction.lower().startswith('received') else 'Debit'))
 elif entity=='supplier':
  obj=Supplier.query.get_or_404(id); title='Supplier Ledger — '+obj.name
  for x in Purchase.query.filter_by(supplier_id=id).all(): rows.append((x.dt,'Purchase',x.invoice,x.total,'Credit'))
  for x in Advance.query.filter_by(supplier_id=id).all(): rows.append((x.dt,'Advance',str(x.id),x.amount,'Debit' if x.direction.lower().startswith('paid') else 'Credit'))
 elif entity=='product':
  obj=Product.query.get_or_404(id); title='Product Ledger — '+obj.name
  for x in Purchase.query.filter_by(product_id=id).all(): rows.append((x.dt,'Purchase',x.invoice,x.qty,'Stock In'))
  for x in Sale.query.filter_by(product_id=id).all(): rows.append((x.dt,'Sales',x.invoice,x.qty,'Stock Out'))
  for x in OpeningStock.query.filter_by(product_id=id).all(): rows.append((x.dt,'Opening Stock',str(x.id),x.qty,'Opening'))
 elif entity=='investor':
  obj=Investor.query.get_or_404(id); title='Investor Ledger — '+obj.name
  for x in Investment.query.filter_by(investor_id=id).all(): rows.append((x.dt,'Investment',str(x.id),x.amount,'Capital'))
 else: abort(404)
 return render_template('entity_ledger.html',title=title,rows=sorted(rows,key=lambda z:z[0],reverse=True))
@app.route('/product-list')
def product_list(): return render_template('product_list.html',rows=Product.query.order_by(Product.name).all())
def cash_account_name(showroom_id=None):
 return 'Cash in Hand' if not showroom_id else 'Cash in Hand - '+str(Showroom.query.get(showroom_id).name if Showroom.query.get(showroom_id) else showroom_id)

def bank_account_name(bank_id):
 b=BankAccount.query.get(bank_id)
 return 'Bank - '+(b.name or b.bank_name or str(bank_id)) if b else 'Bank'

def account_book(showroom_id=None, start=None, end=None):
 """Return normalized double-entry rows: date, account, debit, credit, ref, module, party, showroom."""
 rows=[]
 def add(dt,account,debit=0,credit=0,ref='',module='',party='',sid=None):
  if start and dt and dt<start:return
  if end and dt and dt>end:return
  if showroom_id and sid!=showroom_id:return
  rows.append((dt,account,float(debit or 0),float(credit or 0),ref,module,party,sid))
 # Opening balances
 for x in OpeningBalance.query.all():
  add(x.dt,x.account_name or x.account_type,x.amount if x.direction=='Debit' else 0,x.amount if x.direction=='Credit' else 0,'OPEN-'+str(x.id),'Opening',x.account_name,x.showroom_id)
 # Opening stock
 for x in OpeningStock.query.all():
  v=(x.qty or 0)*(x.unit_cost or 0)
  add(x.dt,'Inventory',v,0,'OS-'+str(x.id),'Opening Stock',x.product.name if x.product else '',x.showroom_id)
  add(x.dt,'Opening Balance Equity',0,v,'OS-'+str(x.id),'Opening Stock','',x.showroom_id)
 # Purchases
 for x in Purchase.query.all():
  add(x.dt,'Inventory',x.total,0,x.invoice,'Purchase',str(x.supplier_id or ''),x.showroom_id)
  if x.payment_type=='Cash': add(x.dt,'Cash in Hand',0,x.total,x.invoice,'Purchase',str(x.supplier_id or ''),x.showroom_id)
  elif x.payment_type=='Bank': add(x.dt,bank_account_name(x.bank_account_id),0,x.total,x.invoice,'Purchase',str(x.supplier_id or ''),x.showroom_id)
  else: add(x.dt,'Supplier Payable',0,x.total,x.invoice,'Purchase',str(x.supplier_id or ''),x.showroom_id)
 # Sales and COGS
 for x in Sale.query.all():
  add(x.dt,'Sales Revenue',0,x.net,x.invoice,'Sales',str(x.customer_id or ''),x.showroom_id)
  if x.payment_type=='Cash': add(x.dt,'Cash in Hand',x.net,0,x.invoice,'Sales',str(x.customer_id or ''),x.showroom_id)
  elif x.payment_type=='Bank': add(x.dt,bank_account_name(x.bank_account_id),x.net,0,x.invoice,'Sales',str(x.customer_id or ''),x.showroom_id)
  elif x.payment_type=='Installment':
   first=x.first_payment or 0; due=max(0,(x.net or 0)-first)
   if first: add(x.dt,'Cash in Hand',first,0,x.invoice,'Sales',str(x.customer_id or ''),x.showroom_id)
   if due: add(x.dt,'Customer Receivable',due,0,x.invoice,'Sales',str(x.customer_id or ''),x.showroom_id)
  elif x.payment_type=='Advance Adjustment': add(x.dt,'Customer Advance',x.net,0,x.invoice,'Sales',str(x.customer_id or ''),x.showroom_id)
  else: add(x.dt,'Customer Receivable',x.net,0,x.invoice,'Sales',str(x.customer_id or ''),x.showroom_id)
  p=Product.query.get(x.product_id); c=(p.purchase_price if p else 0)*(x.qty or 0)
  if c: add(x.dt,'Cost of Goods Sold',c,0,x.invoice,'COGS',p.name if p else '',x.showroom_id); add(x.dt,'Inventory',0,c,x.invoice,'COGS',p.name if p else '',x.showroom_id)
 # Expenses
 for x in Expense.query.all():
  head=x.head.name if x.head else (x.category or 'Expense')
  add(x.dt,head,x.amount,0,'EXP-'+str(x.id),'Expense',x.category,x.showroom_id)
  if x.payment_method=='Bank': add(x.dt,bank_account_name(x.bank_account_id),0,x.amount,'EXP-'+str(x.id),'Expense',x.category,x.showroom_id)
  else: add(x.dt,'Cash in Hand',0,x.amount,'EXP-'+str(x.id),'Expense',x.category,x.showroom_id)
 # Investments
 for x in Investment.query.all():
  target=bank_account_name(x.bank_account_id) if x.method=='Bank' else 'Cash in Hand'
  add(x.dt,target,x.amount,0,'INV-'+str(x.id),'Investment',str(x.investor_id or ''),x.showroom_id); add(x.dt,'Owner/Investor Capital',0,x.amount,'INV-'+str(x.id),'Investment',str(x.investor_id or ''),x.showroom_id)
 # Assets / liabilities (asset entry assumed paid from cash; liability is credit source)
 for x in Asset.query.all():
  add(x.dt,'Asset - '+x.name,x.value,0,'AST-'+str(x.id),'Asset',x.name,x.showroom_id); add(x.dt,'Cash in Hand',0,x.value,'AST-'+str(x.id),'Asset',x.name,x.showroom_id)
 for x in Liability.query.all():
  add(x.dt,'Liability - '+x.name,0,x.amount,'LIA-'+str(x.id),'Liability',x.name,x.showroom_id); add(x.dt,'Cash in Hand',x.amount,0,'LIA-'+str(x.id),'Liability',x.name,x.showroom_id)
 # Loans
 for x in Loan.query.all():
  if x.direction=='Borrowed':
   add(x.dt,'Cash in Hand',x.principal,0,'LOAN-'+str(x.id),'Loan',x.party_name,x.showroom_id); add(x.dt,'Loan Payable',0,x.principal,'LOAN-'+str(x.id),'Loan',x.party_name,x.showroom_id)
  else:
   add(x.dt,'Loan Receivable',x.principal,0,'LOAN-'+str(x.id),'Loan',x.party_name,x.showroom_id); add(x.dt,'Cash in Hand',0,x.principal,'LOAN-'+str(x.id),'Loan',x.party_name,x.showroom_id)
  if x.interest: add(x.dt,'Interest Expense',x.interest,0,'LOAN-'+str(x.id),'Loan Interest',x.party_name,x.showroom_id)
 # Manual cash/bank entries
 for x in CashEntry.query.all(): add(x.dt,'Cash in Hand',x.amount if x.entry_type=='Receipt' else 0,x.amount if x.entry_type=='Payment' else 0,x.reference,'Cash Book',x.party,x.showroom_id)
 for x in BankEntry.query.all(): add(x.dt,bank_account_name(x.bank_account_id),x.amount if x.entry_type=='Receipt' else 0,x.amount if x.entry_type=='Payment' else 0,x.reference,'Bank Book',x.party,x.showroom_id)
 # Installment collections
 for p in InstallmentPayment.query.all():
  inst=Installment.query.get(p.installment_id); sid=None
  if inst and inst.sale_id: sid=Sale.query.get(inst.sale_id).showroom_id
  target=bank_account_name(p.bank_account_id) if p.method=='Bank' else 'Cash in Hand'
  add(p.dt,target,p.amount,0,'IP-'+str(p.id),'Installment Collection','',sid); add(p.dt,'Customer Receivable',0,p.amount,'IP-'+str(p.id),'Installment Collection','',sid)
 return rows

@app.route('/trial-balance')
def trial_balance():
 rows=account_book(); a={}
 for _,acct,d,c,*_ in rows:
  a.setdefault(acct,[0,0]); a[acct][0]+=d; a[acct][1]+=c
 out=[(k,v[0],v[1]) for k,v in sorted(a.items()) if v[0] or v[1]]
 return render_template('trial_balance.html',rows=out,total_debit=sum(r[1] for r in out),total_credit=sum(r[2] for r in out))

@app.route('/balance-sheet')
def balance_sheet():
 rows=account_book(); bal={}
 for _,acct,d,c,*_ in rows: bal[acct]=bal.get(acct,0)+d-c
 assets=[(k,v) for k,v in bal.items() if v>0 and (k.startswith('Asset -') or k in ('Cash in Hand','Inventory','Customer Receivable','Loan Receivable') or k.startswith('Bank -'))]
 liabilities=[(k,-v) for k,v in bal.items() if v<0 and (k.startswith('Liability -') or k in ('Supplier Payable','Customer Advance','Loan Payable'))]
 capital=[(k,-v) for k,v in bal.items() if v<0 and ('Capital' in k or 'Investor' in k)]
 income=sum(-v for k,v in bal.items() if k=='Sales Revenue'); expenses=sum(v for k,v in bal.items() if k=='Cost of Goods Sold' or k=='Interest Expense' or (v>0 and (k in [h.name for h in ExpenseHead.query.all()])))
 profit=income-expenses
 return render_template('balance_sheet.html',assets=assets,liabilities=liabilities,capital=capital,profit=profit,total_assets=sum(v for _,v in assets),total_liabilities=sum(v for _,v in liabilities),total_equity=sum(v for _,v in capital)+profit)

@app.route('/profit-loss')
def profit_loss():
 start=request.args.get('start'); end=request.args.get('end')
 sd=datetime.strptime(start,'%Y-%m-%d').date() if start else None; ed=datetime.strptime(end,'%Y-%m-%d').date() if end else None
 rows=account_book(start=sd,end=ed)
 sales=sum(c for _,a,d,c,*_ in rows if a=='Sales Revenue')
 cogs=sum(d for _,a,d,c,*_ in rows if a=='Cost of Goods Sold')
 direct_heads={h.name for h in ExpenseHead.query.filter_by(expense_type='Direct').all()}; indirect_heads={h.name for h in ExpenseHead.query.filter_by(expense_type='Indirect').all()}
 direct=sum(d for _,a,d,c,*_ in rows if a in direct_heads); indirect=sum(d for _,a,d,c,*_ in rows if a in indirect_heads)
 interest=sum(d for _,a,d,c,*_ in rows if a=='Interest Expense')
 gross=sales-cogs; net=gross-direct-indirect-interest
 return render_template('profit_loss.html',sales=sales,cogs=cogs,gross_profit=gross,direct=direct,indirect=indirect,interest=interest,net_profit=net,start=start or '',end=end or '')

@app.route('/reports')
def reports(): return render_template('reports.html')
@app.route('/change-password',methods=['GET','POST'])
def change_password():
 if request.method=='POST':
  u=User.query.get(session['user_id']); old=request.form['current_password']; new=request.form['new_password']; confirm=request.form['confirm_password']
  if not check_password_hash(u.password_hash,old): flash('Current password is incorrect','danger')
  elif len(new)<6: flash('Password must be at least 6 characters','danger')
  elif new!=confirm: flash('New passwords do not match','danger')
  else: u.password_hash=generate_password_hash(new); db.session.commit(); flash('Password changed successfully','success'); return redirect(url_for('dashboard'))
 return render_template('change_password.html')
@app.route('/admin',methods=['GET','POST'])
def admin_page():
 require_admin()
 if request.method=='POST':
  db.session.add(User(username=request.form['username'],password_hash=generate_password_hash(request.form['password']),role=request.form['role'])); db.session.commit(); flash('User added','success')
 return render_template('admin.html',users=User.query.order_by(User.id).all(),counts={'Showrooms':Showroom.query.count(),'Categories':Category.query.count(),'Products':Product.query.count(),'Customers':Customer.query.count(),'Suppliers':Supplier.query.count()})
@app.route('/admin/user/<int:id>/toggle',methods=['POST'])
def toggle_user(id): require_admin(); u=User.query.get_or_404(id); u.active=not u.active; db.session.commit(); return redirect(url_for('admin_page'))
@app.route('/api/products-by-category/<int:cid>')
def api_products(cid): return [{'id':p.id,'name':p.name,'barcode':p.barcode or ''} for p in Product.query.filter_by(category_id=cid,active=True).order_by(Product.name)]
@app.route('/api/product-by-barcode/<barcode>')
def api_barcode(barcode):
 p=Product.query.filter_by(barcode=barcode,active=True).first(); return ({'id':p.id,'name':p.name,'sale_price':p.sale_price} if p else {'error':'Not found'})
@app.route('/backup')
def backup():
 require_admin(); src=os.path.join(INSTANCE,'shop_accounts.db'); dest=os.path.join(INSTANCE,'backup_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.db'); shutil.copy2(src,dest); flash('Backup created: '+os.path.basename(dest),'success'); return redirect(url_for('dashboard'))

# Admin universal edit/delete for all stored records. Stock is adjusted safely for sale/purchase/opening-stock.
MODEL_MAP={'showroom':Showroom,'category':Category,'product':Product,'customer':Customer,'supplier':Supplier,'investor':Investor,'bank':BankAccount,'sale':Sale,'purchase':Purchase,'expense':Expense,'investment':Investment,'asset':Asset,'liability':Liability,'loan':Loan,'advance':Advance,'opening':OpeningBalance,'opening_stock':OpeningStock,'cash':CashEntry,'bank_entry':BankEntry,'installment':Installment,'expense_head':ExpenseHead}
EDIT_FIELDS={
'showroom':['name','address','manager','contact','active'],'category':['name','active'],'product':['name','category_id','barcode','sku','sale_price','purchase_price','reorder_level','active'],
'customer':['name','mobile','address','reference_name','reference_number','showroom_id','opening_due','opening_advance','active'],'supplier':['name','mobile','address','opening_due','opening_advance','active'],
'investor':['name','mobile','designation','active'],'bank':['name','bank_name','branch','account_no','routing_no','account_type','opening_balance','active'],
'sale':['dt','invoice','showroom_id','customer_id','product_id','qty','unit_price','discount','payment_type','bank_account_id','first_payment','installment_months','installment_start','notes'],
'purchase':['dt','invoice','showroom_id','supplier_id','product_id','qty','unit_price','payment_type','bank_account_id','notes'],
'expense':['dt','showroom_id','head_id','category','amount','payment_method','bank_account_id','notes'],'investment':['dt','showroom_id','investor_id','amount','method','bank_account_id','description'],
'asset':['dt','showroom_id','name','value','notes','active'],'liability':['dt','showroom_id','name','amount','notes','active'],'loan':['dt','showroom_id','party_type','party_id','party_name','principal','paid','interest','due_date','direction','notes','active'],
'advance':['dt','showroom_id','customer_id','supplier_id','amount','adjusted','direction','method','bank_account_id','notes'],'opening':['dt','showroom_id','account_type','account_name','amount','direction','notes'],
'opening_stock':['dt','showroom_id','product_id','qty','unit_cost','notes'],'cash':['dt','showroom_id','entry_type','category','party','amount','reference','notes'],'bank_entry':['dt','showroom_id','bank_account_id','entry_type','category','party','amount','reference','notes'],'installment':['due_date','amount','paid','status'],'expense_head':['name','expense_type','active']}
@app.route('/admin/edit/<model>/<int:id>',methods=['GET','POST'])
def admin_edit(model,id):
 require_admin(); M=MODEL_MAP.get(model); x=M.query.get_or_404(id)
 if request.method=='POST':
  oldqty=getattr(x,'qty',None); oldpid=getattr(x,'product_id',None); oldsid=getattr(x,'showroom_id',None)
  for f in EDIT_FIELDS.get(model,[]):
   if f not in request.form: continue
   v=request.form[f]
   col=getattr(M,f).property.columns[0].type if hasattr(getattr(M,f),'property') else None
   if f=='active': v='active' in request.form
   elif f in ('showroom_id','category_id','customer_id','supplier_id','investor_id','bank_account_id','product_id','party_id','head_id','qty','reorder_level','installment_months','paid'): v=int(v) if v else None
   elif f in ('value','amount','unit_price','discount','first_payment','opening_due','opening_advance','sale_price','purchase_price','opening_balance','principal','interest','adjusted','unit_cost','guarantee_amount'): v=float(v or 0)
   elif f in ('dt','due_date','installment_start') and v: v=datetime.strptime(v,'%Y-%m-%d').date()
   setattr(x,f,v)
  if model=='expense' and f=='head_id':
   h=ExpenseHead.query.get(v) if v else None
   x.category=h.name if h else ''
  if model in ('sale','purchase','opening_stock') and oldqty is not None:
   # rebuild stock impact for changed transaction
   s=stock_for(oldpid,oldsid); s.qty += (-oldqty if model=='sale' else oldqty if model in ('purchase','opening_stock') else 0)
   if model=='sale': stock_for(x.product_id,x.showroom_id).qty-=x.qty
   else: stock_for(x.product_id,x.showroom_id).qty+=x.qty
  db.session.commit(); audit('EDIT',model,str(id)); flash('Updated','success'); return redirect(url_for('admin_page'))
 return render_template('admin_edit.html',model=model,x=x,fields=EDIT_FIELDS.get(model,[]))
@app.route('/admin/delete/<model>/<int:id>',methods=['POST'])
def admin_delete(model,id):
 require_admin(); M=MODEL_MAP.get(model); x=M.query.get_or_404(id)
 if model=='sale': stock_for(x.product_id,x.showroom_id).qty+=x.qty
 elif model in ('purchase','opening_stock'): stock_for(x.product_id,x.showroom_id).qty-=x.qty
 db.session.delete(x); db.session.commit(); audit('DELETE',model,str(id)); flash('Record removed','success'); return redirect(request.referrer or url_for('admin_page'))

if __name__=='__main__': app.run(host='127.0.0.1',port=5000,debug=True)
