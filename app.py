#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import filedialog
import tkinter.messagebox as messagebox
import pandas as pd
import numpy as np
from joblib import load
from sklearn.ensemble import RandomForestClassifier

class FraudDetectionApp:
    def __init__(self, master):
        self.master = master
        self.initialize_gui()
        self.rf_model = load('random_forest_model.joblib')

    def initialize_gui(self):
        # Установка параметров окна
        self.master.geometry("600x300")
        self.master.resizable(width=False, height=False)
        self.master.title("Выявление мошеннических транзакций")

        # Создание описания перед кнопкой
        self.description_label = tk.Label(
            self.master, 
            text=self.get_description_text())
        self.description_label.pack(pady=10)

        # Создание кнопки для загрузки данных
        self.load_button = tk.Button(
            self.master,
            text="Загрузить данные и предсказать",
            command=self.get_prediction)
        self.load_button.pack(pady=20)

    def get_description_text(self):
        description_text = '''
        Для анализа транзакции загрузите csv-файл

        Файл должен состоять из граф в следующем порядке: 
        Время транзакции (час транзации), зашифрованные данные из 28 граф, сумма транзакции
        '''
        return description_text

    def get_prediction(self):
        data = self.load_data()
        if data.empty:
            return
        if self.check_form(data):
            self.predict(data)

    def load_data(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        if not file_path.lower().endswith('.csv'):
            messagebox.showerror(
                "Ошибка",
                "Неверный формат файла. Файл должен быть в формате CSV.")
            return
        try:
            has_header = messagebox.askyesno(
                "Заголовок в файле", 
                "Файл содержит заголовок?")
            if has_header:
                data = pd.read_csv(file_path)
            else:
                data = pd.read_csv(file_path, header=None)
        except Exception as e:
            messagebox.showerror(
                "Ошибка",
                f"Возникла ошибка при чтении данных: {e}")
            return
        else:
            return data

    def check_form(self, data):
        if data.shape[1] != 30:
            messagebox.showerror(
                "Ошибка",
                "Должно быть 30 столбцов в файле.\n"
                + "Сейчас cтолбцов: " + str(data.shape[1]))
            return

        try:
            data.iloc[:, 0].astype(int)
        except ValueError:
            messagebox.showerror(
                "Ошибка",
                "Первый столбец должен содержать ифнормацию о часе транзакции, "
                + "число от 0 до 23 (часы).")
            return

        if not data.iloc[:, 0].between(0, 23).all():
            messagebox.showerror(
                "Ошибка",
                "Первый столбец должен содержать ифнормацию о часе транзакции, "
                + "число от 0 до 23 (часы).")
            return
        
        if not all(data.iloc[:, 1:30].apply(pd.api.types.is_numeric_dtype).values):
            messagebox.showerror(
                "Ошибка",
                "Столбцы с 2 по 30 должны быть числовыми.")
            return
        
        return True

    def predict(self, data):
        columns_name = ['Hour'] + [f'V{i}' for i in range(1, 29)] + ['Amount']
        data.columns = columns_name
        data['Amount_log'] = np.log1p(data.iloc[:, 29])
        dict_predictions = {0: 'немошенническая', 1: 'мошенническая'}
        predictions = self.rf_model.predict(data)
        new_threshold = 0.2
        predictions_new_threshold = (predictions >= new_threshold).astype(int)
        
        if data.shape[0] == 1:
            prediction_phrase = dict_predictions[predictions_new_threshold[0]]
            messagebox.showinfo(
                "Предсказание",
                "В файле обнаруженая одна запись\n" +
                f"Модель определяет транзацию как {prediction_phrase}")
            
        if data.shape[0] >= 2:
            data_with_predictions = pd.concat(
                [data,
                 pd.DataFrame(predictions_new_threshold, columns=['Prediction'])
                 ]
                , axis=1)
            data_with_predictions.to_csv('predictions.csv', index=False)
            messagebox.showinfo(
                "Сохранение",
                "Данные с предсказаниями сохранены в файл predictions.csv")

def main():
    root = tk.Tk()
    app = FraudDetectionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()