def setup(worksheet, itemCount):
    amount = itemCount - 7
    
    # Variables for initial row numbers
    first_row = 16                  # The first item row is 16
    initial_last_item_row = 24

    
    
    
    # Variables for initial column numbers
    
    
    new_last_row = initial_last_item_row + amount
    
    """
    Unmerge...
        - Row [27], Colummns [C, D, E, F, G, H]
    """
    # Unmerge the "Notes" rows
    worksheet.unmerge_cells("C27:H27")
    worksheet.unmerge_cells("B28:H28")
    worksheet.unmerge_cells("B29:H29")
    worksheet.unmerge_cells("B30:H30")
    worksheet.unmerge_cells("B31:H31")
    
    # Unmerge the "Total" cells
    worksheet.unmerge_cells("I30:I31")
    worksheet.unmerge_cells(start_row=30, start_column=10, end_row=31, end_column=11)
    
    worksheet.merge_cells("J30:K30")
    worksheet.merge_cells("J31:K31")

    
    # Add `amount` rows before row 24
    worksheet.insert_rows(initial_last_item_row, amount=amount)
    
    for row in range(initial_last_item_row, new_last_row+1):
        return
    
    # Merge new "Notes" cells    
    worksheet.merge_cells(f"C{27+amount}:H{27+amount}")
    worksheet.merge_cells(f"B{28+amount}:H{28+amount}")
    worksheet.merge_cells(f"B{29+amount}:H{29+amount}")
    worksheet.merge_cells(f"B{30+amount}:H{30+amount}")
    worksheet.merge_cells(f"B{31+amount}:H{31+amount}")
    
    # Merge new 
    worksheet.merge_cells(f"I{30+amount}:I{31+amount}")
    start_row = 30 + amount
    end_row = 31 + amount
    worksheet.merge_cells(start_row=start_row, start_column=10, end_row=end_row, end_column=11)
    
    worksheet.unmerge_cells(f"J{30+amount}:J{31+amount}")
    worksheet.unmerge_cells(f"K{30+amount}:K{31+amount}")