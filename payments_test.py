from yoomoney import Client, Quickpay


token = "4100118665757287.475B87DB7EF0F72B72D6E92EDE632D61D38DA61C7F0E2C6F81C0FF31B919E395B870EA9805CA802A65556307C3EA347CD17897E58F5F34621E0A214C7129A4D58B3BF0FEBA05318C3A027FE99BC858BE2E042177D96CB50BA96982ED13CBB8AD59EFDC9B51827CDBCC282E891D30AD62F1FE994DB1441638493B93AABD86C479"

quickpay = Quickpay(
            receiver="410019014512803",
            quickpay_form="shop",
            targets="Sponsor this project",
            paymentType="SB",
            sum=150,
            label="a1b2c3d4e5"
            )
print(quickpay.base_url)
print(quickpay.redirected_url)


client = Client(token)
history = client.operation_history()
print("List of operations:")
print("Next page starts with: ", history.next_record)
for operation in history.operations:
    print()
    print("Operation:",operation.operation_id)
    print("\tStatus     -->", operation.status)
    print("\tDatetime   -->", operation.datetime)
    print("\tTitle      -->", operation.title)
    print("\tPattern id -->", operation.pattern_id)
    print("\tDirection  -->", operation.direction)
    print("\tAmount     -->", operation.amount)
    print("\tLabel      -->", operation.label)
    print("\tType       -->", operation.type)