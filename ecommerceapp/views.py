from django.http import HttpResponse
from django.shortcuts import render,redirect
from ecommerceapp.models import Contact,Product,Orders,OrderUpdate
from django.contrib import messages
from math import ceil
from django.conf import settings
import json
import razorpay
from django.views.decorators.csrf import csrf_protect

# Create your views here.

def index(request):

    allProds = []
    catprods = Product.objects.values('category','id')
    print(catprods)
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod= Product.objects.filter(category=cat)
        n=len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    params= {'allProds':allProds}

    return render(request,"index.html",params)

    
def contact(request):
    if request.method=="POST":
        name=request.POST.get("name")
        email=request.POST.get("email")
        desc=request.POST.get("desc")
        pnumber=request.POST.get("pnumber")
        myquery=Contact(name=name,email=email,desc=desc,phonenumber=pnumber)
        myquery.save()
        messages.info(request,"we will get back to you soon..")
        return render(request,"contact.html")


    return render(request,"contact.html")

def about(request):
    return render(request,"about.html")



def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try Again")
        return redirect('/auth/login')

    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = int(request.POST.get('amt')) *100
        razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2','')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        client = razorpay.Client(auth =('rzp_test_Awv5NXO8sP4Ddb','TOf3WiJxqVuA9MdZcwEWXWSL'))
        response_payment = client.order.create(dict(amount =amount,currency ='INR'))
        print(response_payment)
        order_id = response_payment['id']
        print(order_id)
        Order = Orders(order_id=order_id,razorpay_payment_id=razorpay,items_json=items_json,name=name,amount=amount, email=email, address1=address1,address2=address2,city=city,state=state,zip_code=zip_code,phone=phone)
        Order.save()
        oder_status = response_payment['status']
        print(oder_status)
        if oder_status == 'created':
            update = OrderUpdate(order_id=order_id,update_desc="the order has been placed")
            update.save()
            response_payment['name'] = name
            thank = True
            return render(request, 'checkout.html', { 'payment': response_payment})
    return render(request, 'checkout.html')

@csrf_protect
def payment_status(request):
    response =request.POST
    params_dict ={
        'razorpay_payment_id': response['razorpay_payment_id'],
        'razorpay_order_id': response['razorpay_order_id'],
        'razorpay_payment_status': response.get('razorpay_payment_status', ''),  # Use get() with a default value
        'razorpay_signature': response['razorpay_signature'],
        'razorpay_key_version': response.get('razorpay_key_version', ''),  # Use get() with a default value
    }
    client = razorpay.Client(auth =('rzp_test_Awv5NXO8sP4Ddb','TOf3WiJxqVuA9MdZcwEWXWSL'))
    try:
        status =client.utility.verify_payment_signature(params_dict)
        update_id = Orders.objects.get(order_id =response['razorpay_order_id'] )
        update_id.razorpay_payment_id =response['razorpay_payment_id']
        update_id.razorpay_signature =response['razorpay_signature']
        update_id.paid =True
        update_id.save()
        return render(request, 'payment_status.html', {'status':True})
    except:   
        return render(request, 'payment_status.html', {'status':False})
     

    

def profile(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/auth/login')

    currentuser = request.user.username
    items = Orders.objects.filter(email=currentuser)
    rid = ""
    for i in items:
        myid = str(i.id) + "ShopyCart"
        if "ShopyCart" in myid:
            rid = myid.replace("ShopyCart", "")
        print(rid)

    if rid:
        status = OrderUpdate.objects.filter(order_id=int(rid))
        for j in status:
            print(j.update_desc)
    else:
        status = []

    context = {"items": items, "status": status}
    return render(request, "profile.html", context)
