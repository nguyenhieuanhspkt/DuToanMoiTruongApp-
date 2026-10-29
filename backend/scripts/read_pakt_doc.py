import win32com.client
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

doc_path = r'D:\onedrive_hieuna\OneDrive - EVN\Tổ Thẩm định\Năm 2026\Thẩm định 345_hieuna\PAKT\email 28-10-2026 của KTAT\PAKT cần bóc tách .doc'

word = None
try:
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    doc = word.Documents.Open(doc_path)
    
    text = doc.Content.Text
    print(f"Total length: {len(text)}")
    
    # Search for 2.1.2 or san thao tac or van chuyen
    keywords = ["2.1.2", "sàn thao tác", "lỗ lấy mẫu", "di chuyển", "phương tiện", "vận chuyển"]
    for kw in keywords:
        pos = text.lower().find(kw.lower())
        print(f"Keyword '{kw}': pos = {pos}")
        if pos != -1:
            snippet = text[max(0, pos-100):min(len(text), pos+400)]
            print(f"--- Snippet for '{kw}' ---:\n{snippet}\n")
            
    doc.Close(False)
except Exception as e:
    print("Error reading doc:", e)
finally:
    if word:
        word.Quit()
