def calculate_taxes(tpa, ss, qty):
        total_product_amount = float(tpa)
        shipping_state = ss
        quantity=qty
        tax_threshold = 1000  

        if shipping_state == 'WB': 
            if total_product_amount < tax_threshold:
                combined_rate = 0.05  # 2.5% SGST + 2.5% CGST
            else:
                combined_rate = 0.12  # 6% SGST + 6% CGST

        else:  
            if total_product_amount < tax_threshold:
                combined_rate = 0.05  # 5% IGST
            else:
                combined_rate = 0.12  # 12% IGST

        base_price = total_product_amount / (1 + combined_rate)  
        tax_amount = base_price * combined_rate  

    
        if shipping_state == 'WB':
            sgst = tax_amount / 2
            cgst = tax_amount / 2
            igst = 0  
        else:
            sgst = 0
            cgst = 0
            igst = tax_amount 
            
        grand_total = (base_price + tax_amount) * quantity
        subtotal = base_price * quantity
        sgst = sgst * quantity
        cgst = cgst * quantity
        igst = igst * quantity
        tax_amount = tax_amount * quantity

        print("*** Tax Calculation Results ***")
        print(f"Shipping State: {shipping_state}")
        print(f"Quantity: {quantity}")
        print(f"MRP (per unit): ₹{total_product_amount:.2f}")
        print(f"Base Price (per unit): ₹{base_price:.2f}")
        
        if shipping_state == 'WB':
            if total_product_amount < 1000:
                sgst_rate = 2.5
                cgst_rate = 2.5
            else:
                sgst_rate = 6
                cgst_rate = 6
            print(f"SGST ({sgst_rate}%): ₹{sgst:.2f}")
            print(f"CGST ({cgst_rate}%): ₹{cgst:.2f}")
            print(f"IGST: ₹{igst:.2f}") 

        else:  
            if total_product_amount < 1000:
                igst_rate = 5 
            else:
                igst_rate = 12
            print(f"SGST: ₹{sgst:.2f}")
            print(f"CGST: ₹{cgst:.2f}")
            print(f"IGST ({igst_rate}%): ₹{igst:.2f}") 
                
        print(f"Subtotal (excluding tax): ₹{subtotal:.2f}")
        print(f"Total Tax: ₹{tax_amount:.2f}")
        print(f"Grand Total (including tax): ₹{grand_total:.2f}")
        
calculate_taxes(1, 'WB', 1)