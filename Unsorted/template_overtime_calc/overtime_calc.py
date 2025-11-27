import customtkinter as ctk
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from fpdf import FPDF
from tkinter import filedialog, messagebox

# -----------------------------------------------------------------------
# LANG PACK
# -----------------------------------------------------------------------
LANG = {
    "AZ": {
        "title": "OverTime Calc – Corporate Edition",
        "subtitle": "Aylıq maaş və overtime kalkulyatoru",
        "net_salary": "Net maaş",
        "contract_hours": "Aylıq rəsmi iş saatı",
        "currency": "Valyuta",
        "ot_table": "Overtime cədvəli",
        "type": "Növ",
        "hours": "Saat",
        "multiplier": "Çarpan",
        "workday": "İş günü",
        "weekend": "Həftəsonu",
        "holiday": "Bayram",
        "calculate": "Hesabla",
        "excel": "Excel export",
        "pdf": "PDF export",
        "chart": "Qrafik göstər",
        "chart_title": "Maaşın bölgüsü",
        "msg_calc_first": "Əvvəlcə hesablama aparın.",
        "msg_err": "Yanlış input var.",
        "result": (
            "Toplam saat: {total_hours}\n"
            "İş günü OT: {workday_pay} {cur}\n"
            "Həftəsonu OT: {weekend_pay} {cur}\n"
            "Bayram OT: {holiday_pay} {cur}\n"
            "Ümumi maaş: {total_pay} {cur}"
        )
    },
    "EN": {
        "title": "OverTime Calc – Corporate Edition",
        "subtitle": "Corporate salary & overtime calculator",
        "net_salary": "Net Salary",
        "contract_hours": "Contract Hours",
        "currency": "Currency",
        "ot_table": "Overtime Table",
        "type": "Type",
        "hours": "Hours",
        "multiplier": "Multiplier",
        "workday": "Workday",
        "weekend": "Weekend",
        "holiday": "Holiday",
        "calculate": "Calculate",
        "excel": "Export Excel",
        "pdf": "Export PDF",
        "chart": "Show Chart",
        "chart_title": "Salary breakdown",
        "msg_calc_first": "Please calculate first.",
        "msg_err": "Invalid numeric input.",
        "result": (
            "Total Hours: {total_hours}\n"
            "Workday OT: {workday_pay} {cur}\n"
            "Weekend OT: {weekend_pay} {cur}\n"
            "Holiday OT: {holiday_pay} {cur}\n"
            "Total Salary: {total_pay} {cur}"
        )
    },
    "RU": {
        "title": "OverTime Calc – Корпоративная версия",
        "subtitle": "Калькулятор зарплаты и сверхурочных",
        "net_salary": "Чистая зарплата",
        "contract_hours": "Рабочие часы",
        "currency": "Валюта",
        "ot_table": "Таблица сверхурочных",
        "type": "Тип",
        "hours": "Часы",
        "multiplier": "Множитель",
        "workday": "Рабочие дни",
        "weekend": "Выходные",
        "holiday": "Праздники",
        "calculate": "Рассчитать",
        "excel": "Экспорт Excel",
        "pdf": "Экспорт PDF",
        "chart": "Показать график",
        "chart_title": "Разделение зарплаты",
        "msg_calc_first": "Сначала выполните расчёт.",
        "msg_err": "Некорректный ввод.",
        "result": (
            "Всего часов: {total_hours}\n"
            "Рабочие дни OT: {workday_pay} {cur}\n"
            "Выходные OT: {weekend_pay} {cur}\n"
            "Праздники OT: {holiday_pay} {cur}\n"
            "Итоговая зарплата: {total_pay} {cur}"
        )
    }
}

CURRENCIES = ["AZN", "USD", "EUR", "TRY", "RUB", "GBP"]

# -----------------------------------------------------------------------
# MAIN APP
# -----------------------------------------------------------------------
class OverTimeCalc(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.lang = "AZ"
        self.data = {}

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.title("OverTime Calc PRO")
        self.geometry("880x720")
        self.build_ui()
        self.apply_lang()

    # -------------------------------------------------------------------
    # UI BUILD
    # -------------------------------------------------------------------
    def build_ui(self):

        # ---------------------------------------
        # HEADER
        # ---------------------------------------
        head = ctk.CTkFrame(self, fg_color="transparent")
        head.pack(fill="x", pady=10, padx=20)

        self.lbl_title = ctk.CTkLabel(head, text="", font=("Arial", 26, "bold"))
        self.lbl_title.pack(side="left")

        # LANG BUTTONS
        lang_box = ctk.CTkFrame(head, fg_color="transparent")
        lang_box.pack(side="right")

        for code in ["AZ", "EN", "RU"]:
            ctk.CTkButton(
                lang_box, text=code, width=40,
                command=lambda c=code: self.change_lang(c)
            ).pack(side="left", padx=4)

        # SUBTITLE
        self.lbl_sub = ctk.CTkLabel(self, text="", font=("Arial", 14))
        self.lbl_sub.pack(pady=5)

        # ---------------------------------------
        # MONTHLY INPUTS
        # ---------------------------------------
        box = ctk.CTkFrame(self)
        box.pack(fill="x", padx=20, pady=10)

        self.en_salary = ctk.CTkEntry(box, placeholder_text="")
        self.en_salary.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.en_hours = ctk.CTkEntry(box, placeholder_text="")
        self.en_hours.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.lbl_cur = ctk.CTkLabel(box, text="")
        self.lbl_cur.grid(row=1, column=0, padx=10)

        self.en_currency = ctk.CTkOptionMenu(box, values=CURRENCIES)
        self.en_currency.set("AZN")
        self.en_currency.grid(row=1, column=1, padx=10)

        box.grid_columnconfigure(0, weight=1)
        box.grid_columnconfigure(1, weight=1)

        # ---------------------------------------
        # OVERTIME TABLE
        # ---------------------------------------
        table = ctk.CTkFrame(self, corner_radius=12)
        table.pack(fill="x", padx=20, pady=10)

        self.lbl_ot = ctk.CTkLabel(table, text="", font=("Arial", 16, "bold"))
        self.lbl_ot.grid(row=0, column=0, columnspan=3, pady=10)

        self.h_type = ctk.CTkLabel(table, text="")
        self.h_type.grid(row=1, column=0)

        self.h_hours = ctk.CTkLabel(table, text="")
        self.h_hours.grid(row=1, column=1)

        self.h_mult = ctk.CTkLabel(table, text="")
        self.h_mult.grid(row=1, column=2)

        # Workday
        self.lbl_wd = ctk.CTkLabel(table, text="")
        self.lbl_wd.grid(row=2, column=0)

        self.en_wd = ctk.CTkEntry(table, width=120)
        self.en_wd.grid(row=2, column=1)

        self.mul_wd = ctk.CTkOptionMenu(table, values=["1.0", "1.5", "2.0"])
        self.mul_wd.set("1.5")
        self.mul_wd.grid(row=2, column=2)

        # Weekend
        self.lbl_we = ctk.CTkLabel(table, text="")
        self.lbl_we.grid(row=3, column=0)

        self.en_we = ctk.CTkEntry(table, width=120)
        self.en_we.grid(row=3, column=1)

        self.mul_we = ctk.CTkOptionMenu(table, values=["1.0", "1.5", "2.0"])
        self.mul_we.set("2.0")
        self.mul_we.grid(row=3, column=2)

        # Holiday
        self.lbl_hd = ctk.CTkLabel(table, text="")
        self.lbl_hd.grid(row=4, column=0)

        self.en_hd = ctk.CTkEntry(table, width=120)
        self.en_hd.grid(row=4, column=1)

        self.mul_hd = ctk.CTkOptionMenu(table, values=["1.0", "1.5", "2.0"])
        self.mul_hd.set("2.0")
        self.mul_hd.grid(row=4, column=2)

        # ---------------------------------------
        # CALCULATE BUTTON
        # ---------------------------------------
        self.btn_calc = ctk.CTkButton(self, text="", command=self.calculate)
        self.btn_calc.pack(pady=15)

        # RESULT
        self.lbl_res = ctk.CTkLabel(self, text="", font=("Arial", 15))
        self.lbl_res.pack(pady=5)

        # ---------------------------------------
        # EXPORT / CHART
        # ---------------------------------------
        bottom = ctk.CTkFrame(self)
        bottom.pack(pady=10)

        self.btn_xlsx = ctk.CTkButton(bottom, text="", width=150, command=self.export_excel)
        self.btn_xlsx.grid(row=0, column=0, padx=10)

        self.btn_pdf = ctk.CTkButton(bottom, text="", width=150, command=self.export_pdf)
        self.btn_pdf.grid(row=0, column=1, padx=10)

        self.btn_chart = ctk.CTkButton(bottom, text="", width=150, command=self.show_chart)
        self.btn_chart.grid(row=0, column=2, padx=10)

    # -------------------------------------------------------------------
    # LANGUAGE APPLY
    # -------------------------------------------------------------------
    def change_lang(self, lang):
        self.lang = lang
        self.apply_lang()

    def apply_lang(self):
        L = LANG[self.lang]

        self.lbl_title.configure(text=L["title"])
        self.lbl_sub.configure(text=L["subtitle"])

        self.en_salary.configure(placeholder_text=L["net_salary"])
        self.en_hours.configure(placeholder_text=L["contract_hours"])

        self.lbl_cur.configure(text=L["currency"])

        self.lbl_ot.configure(text=L["ot_table"])
        self.h_type.configure(text=L["type"])
        self.h_hours.configure(text=L["hours"])
        self.h_mult.configure(text=L["multiplier"])

        self.lbl_wd.configure(text=L["workday"])
        self.lbl_we.configure(text=L["weekend"])
        self.lbl_hd.configure(text=L["holiday"])

        self.btn_calc.configure(text=L["calculate"])
        self.btn_xlsx.configure(text=L["excel"])
        self.btn_pdf.configure(text=L["pdf"])
        self.btn_chart.configure(text=L["chart"])

    # -------------------------------------------------------------------
    # CALCULATION
    # -------------------------------------------------------------------
    def calculate(self):
        L = LANG[self.lang]

        try:
            sal = float(self.en_salary.get())
            hrs = float(self.en_hours.get())

            wd = float(self.en_wd.get() or 0)
            we = float(self.en_we.get() or 0)
            hd = float(self.en_hd.get() or 0)

            m1 = float(self.mul_wd.get())
            m2 = float(self.mul_we.get())
            m3 = float(self.mul_hd.get())

        except Exception:
            messagebox.showerror("Error", L["msg_err"])
            return

        if hrs <= 0:
            messagebox.showerror("Error", L["msg_err"])
            return

        rate = sal / hrs

        wd_pay = wd * rate * m1
        we_pay = we * rate * m2
        hd_pay = hd * rate * m3

        total_hours = hrs + wd + we + hd
        total_pay = sal + wd_pay + we_pay + hd_pay
        currency = self.en_currency.get()

        self.data = {
            "salary": sal,
            "hours": hrs,
            "wd_pay": wd_pay,
            "we_pay": we_pay,
            "hd_pay": hd_pay,
            "total_hours": total_hours,
            "total_pay": total_pay,
            "currency": currency
        }

        self.lbl_res.configure(
            text=L["result"].format(
                total_hours=f"{total_hours:.2f}",
                workday_pay=f"{wd_pay:.2f}",
                weekend_pay=f"{we_pay:.2f}",
                holiday_pay=f"{hd_pay:.2f}",
                total_pay=f"{total_pay:.2f}",
                cur=currency
            )
        )

    # -------------------------------------------------------------------
    # EXCEL EXPORT
    # -------------------------------------------------------------------
    def export_excel(self):
        if not self.data:
            messagebox.showinfo("Info", LANG[self.lang]["msg_calc_first"])
            return

        file = filedialog.asksaveasfilename(defaultextension=".xlsx")
        if not file:
            return

        pd.DataFrame([self.data]).to_excel(file, index=False)
        messagebox.showinfo("OK", "Excel exported.")

    # -------------------------------------------------------------------
    # PDF EXPORT
    # -------------------------------------------------------------------
    def export_pdf(self):
        if not self.data:
            messagebox.showinfo("Info", LANG[self.lang]["msg_calc_first"])
            return

        file = filedialog.asksaveasfilename(defaultextension=".pdf")
        if not file:
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "OverTime Calc – Report", ln=True)

        pdf.set_font("Arial", size=12)
        for k, v in self.data.items():
            pdf.cell(0, 8, f"{k}: {v}", ln=True)

        pdf.output(file)
        messagebox.showinfo("OK", "PDF exported.")

    # -------------------------------------------------------------------
    # USER-FRIENDLY CHART
    # -------------------------------------------------------------------
    def show_chart(self):

        if not self.data:
            messagebox.showinfo("Info", LANG[self.lang]["msg_calc_first"])
            return

        labels = ["Base", "Workday OT", "Weekend OT", "Holiday OT"]
        values = [
            self.data["salary"],
            self.data["wd_pay"],
            self.data["we_pay"],
            self.data["hd_pay"]
        ]

        colors = plt.colormaps["Set2"](np.linspace(0.15, 0.85, len(labels)))

        fig, ax = plt.subplots(figsize=(8.5, 5.5))
        bars = ax.bar(labels, values, color=colors, edgecolor="#2b2b2b")

        ax.set_ylabel(f"{LANG[self.lang]['currency']} ({self.data['currency']})", fontsize=12)
        ax.set_title(LANG[self.lang]["chart_title"], fontsize=16, weight="bold")
        ax.grid(axis="y", linestyle="--", alpha=0.6)

        max_height = max(values) if values else 0
        offset = max_height * 0.02 if max_height else 1

        for bar, value in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + offset,
                f"{value:.2f}",
                ha="center",
                va="bottom",
                fontsize=11,
                weight="bold"
            )

        plt.tight_layout()
        plt.show()


# RUN APP
if __name__ == "__main__":
    OverTimeCalc().mainloop()
