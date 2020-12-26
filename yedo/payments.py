import stripe

from yedo.settings import DOMAIN, S_T_R_I_P_E_KEY
stripe.api_key = S_T_R_I_P_E_KEY


def newPayment(name, desc, img_url, amount, employeur, type, days=0):
    customer = None
    if employeur.stripe_id:
        customer = stripe.Customer.retrieve(employeur.stripe_id)
    else:
        customer = stripe.Customer.create(
            description="Customer for " + str(employeur.user.email) + " !",
            email=employeur.user.email
        )
        employeur.stripe_id = customer.id
        employeur.save()


    return stripe.checkout.Session.create(
        customer=customer,
        payment_method_types=['card'],
        line_items=[{
            'name': name,
            'description': desc,
            'images': [img_url],
            'amount': amount,
            'currency': 'eur',
            'quantity': 1,
        }],
        payment_intent_data={
            'metadata': {
                'employeur_id': employeur.id,
                'type': type,
                'days': days
            }
        },
        client_reference_id= employeur.id,
        success_url= DOMAIN + '/payment/success/',
        cancel_url= DOMAIN + '/payment/canceled/',
    )
#
# def newSubscription(employeur):
#     customer = None
#     if employeur.stripe_id:
#         customer = stripe.Customer.retrieve(employeur.stripe_id)
#     else:
#         customer = stripe.Customer.create(
#             description="Customer for " + str(employeur.user.email) + " !",
#             email = employeur.user.email,
#             plan = "plan_FqBukJVZF1dcUd"
#         )
#         employeur.stripe_id = customer.id
#         employeur.save()
#     print(customer)
#
#     return stripe.Subscription.create(
#         customer=customer,
#         items=[
#             {
#                 "plan": "plan_FqBukJVZF1dcUd",
#             },
#         ]
#     )