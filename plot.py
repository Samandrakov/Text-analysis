import tkinter as tk
from tkinter import ttk
from nltk.tokenize import sent_tokenize, word_tokenize
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter


def get_word_frequency():
    global text_parts, word_freq, word_list
    text = text_entry.get("1.0", tk.END)

    # Разбиение текста на 10 частей (или ближе к 10)
    words = word_tokenize(text)
    text_parts = []
    part_size = len(words) // 10
    for i in range(0, len(words), part_size):
        text_parts.append(' '.join(words[i:i + part_size]))

    # Подсчет частоты каждого слова в тексте
    word_freq = dict(Counter(words))

    # Заполнение listbox словами и их частотами
    sorted_word_freq = dict(sorted(word_freq.items(), key=lambda item: item[1], reverse=True))
    word_list = list(sorted_word_freq.keys())
    word_combobox.delete(0, tk.END)
    for word in word_list:
        word_combobox.insert(tk.END, f"{word} ({word_freq[word]})")


def plot_word_usage():
    global old_canvas
    # Очистка предыдущих графиков
    if old_canvas:
        old_canvas.get_tk_widget().destroy()
    selected_items = word_combobox.curselection()
    fig, ax = plt.subplots(figsize=(8, 5))

    for idx in selected_items:
        selected_item = word_list[int(idx)]
        word_part_freq = []
        for part in text_parts:
            words = word_tokenize(part)
            total_words = len(words)
            word_count = words.count(selected_item)
            relative_freq = word_count / total_words if total_words > 0 else 0
            word_part_freq.append(relative_freq)

        ax.plot(range(1, len(text_parts) + 1), word_part_freq, marker='o', linestyle='-', label=f'{selected_item}')

        for i, freq in enumerate(word_part_freq, start=1):
            ax.text(i, freq, f'{freq:.2f}', ha='center', va='bottom', fontsize=8)

    ax.set_xlabel('Части текста')
    ax.set_ylabel('Относительная частота слова')
    ax.set_title(f'Относительная частота слов в частях текста')
    ax.legend()

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    old_canvas = canvas


root = tk.Tk()
root.title("Анализатор текста")

text_entry = tk.Text(root, width=40, height=10)
text_entry.pack(padx=10, pady=10)

analyze_button = tk.Button(root, text="Анализировать текст", command=get_word_frequency)
analyze_button.pack(pady=10)

word_combobox = tk.Listbox(root, selectmode=tk.EXTENDED)
word_combobox.pack(pady=10)

plot_button = tk.Button(root, text="Построить график", command=plot_word_usage)
plot_button.pack(pady=10)

old_canvas = None  # Хранит ссылку на предыдущий холст

root.mainloop()
