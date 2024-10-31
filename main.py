import pandas as pd
import random
from datetime import datetime
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# 定义一个函数来读取和初始化单词库
def load_words(filepath):
    # 使用 pandas 读取表格数据，同时跳过空行
    words_df = pd.read_csv(filepath, skip_blank_lines=True)

    # 检查并添加缺失的列，设置默认值
    if '选中次数' not in words_df.columns:
        words_df['选中次数'] = 0

    if '正确次数' not in words_df.columns:
        words_df['正确次数'] = 0

    if '是否训练' not in words_df.columns:
        words_df['是否训练'] = 1

    return words_df


# 定义一个函数作为训练开始前的设置
def setup_training(words_df):
    def start_callback():
        try:
            num_words = int(entry.get())
            if num_words <= 0 or num_words > len(words_df):
                # 如果输入的数字小于等于0或者大于单词总数，显示错误提示
                error_label.config(text=f"输入有效数量！1-{len(words_df)}")
            else:
                # 如果输入的数字是有效的，关闭设置窗口
                setup_window.withdraw()
                selected_words = select_words(words_df, num_words)
                start_training(selected_words, setup_window)


        except ValueError:
            # 如果输入不是一个整数，显示错误提示
            error_label.config(text="请输入一个整数！")

    # 创建设置窗口
    setup_window = ttk.Window(
        title="汪涵背单词V1.0 - Setting",  # 设置窗口的标题
        themename='darkly',  # 设置主题
        size=(400, 300),  # 窗口的大小
        position=(1000, 500),  # 窗口所在的位置
        minsize=(400, 300),  # 窗口的最小宽高
        maxsize=(400, 300),  # 窗口的最大宽高
        alpha=1.0,  # 设置窗口的透明度(0.0完全透明）
    )
    setup_window.iconbitmap('icon.ico')

    # 创建输入框标签、输入框、错误提示标签以及开始按钮
    label = ttk.Label(setup_window, text="本次练习单词数量：")

    entry = ttk.Entry(setup_window)
    entry.insert(0, "200")
    error_label = ttk.Label(setup_window, text="")

    # style2 = ttk.Style()
    # style2.configure('Custom.TButton', font=("Arial", 16), padding=10)


    start_button = ttk.Button(setup_window,
                              text="开始",
                              # style='Custom.TButton',
                              command=start_callback,
                              bootstyle=WARNING
                              )
    ifo_frame = ttk.Label(setup_window, text=f"词库总量：{len(words_df)}")
    blank_frame = ttk.Frame(setup_window)

    setup_window.grid_columnconfigure(0, weight=1)
    # setup_window.grid_rowconfigure(0, weight=1)
    # 将部件布局到窗口
    ifo_frame.grid(row=0, column=0, sticky="w")
    blank_frame.grid(row=1, column=0,pady=20, sticky="n")
    label.grid(row=2, column=0, pady=10, sticky="n")
    entry.grid(row=3, column=0, pady=10, sticky="n")
    error_label.grid(row=4, column=0, sticky="n")
    start_button.grid(row=5, column=0, pady=60, sticky="s")

    setup_window.bind('<Return>', lambda event: start_callback())

    setup_window.mainloop()
    # 运行主循环，显示设置窗口



# 定义一个函数来从单词库中随机选择单词
def select_words(words_df, num_words):
    # 筛选出所有可供训练的单词，即“是否训练”列为1的单词
    trainable_words = words_df[words_df['是否训练'] == 1]

    # 如果请求的单词数量超过了可供训练的单词数量，
    # 就限制它为可供训练的单词数量
    num_words = min(num_words, len(trainable_words))

    # 从可供训练的单词中随机选择指定数量的单词
    selected_words = trainable_words.sample(n=num_words)

    # 返回被选择的单词集（一个DataFrame）
    return selected_words.reset_index(drop=True)


# 定义一个函数来创建练习界面，并展示单词
current_index = 0  # 当前运行到第几个单词的全局计数器
know_count = 0
def start_training(selected_words, window):
    global current_index
    global know_count

    def acknowledge_word(known):
        nonlocal selected_words
        global current_index
        global know_count
        # 更新单词的选中次数和（如果认识该单词则）正确次数
        selected_words.at[current_index, '选中次数'] += 1

        if known:
            know_count += 1
            selected_words.at[current_index, '正确次数'] += 1
        meaning_label.config(text=f"{selected_words.at[current_index, '解释']}")
        ifo_label.config(text=f"历史记录：{words_df.at[current_index, '选中次数']}/{words_df.at[current_index, '正确次数']}")
        known_button.pack_forget()
        unknown_button.pack_forget()
        next_button.pack()
        current_index += 1

    def next_word():
        global current_index
        if current_index < len(selected_words):
            update_word_display()
        else:
            # 如果已经显示了所有选中的单词，结束练习
            finish_training(window)

    def update_word_display():
        ifo_label.config(text=f"当前进度：{current_index}({know_count})/{len(selected_words)}")
        word_display.config(text=f"{selected_words.at[current_index, '单词']}")
        meaning_label.config(text="")
        next_button.pack_forget()
        known_button.pack(side='left', expand=True, fill='x', padx=5)
        unknown_button.pack(side='right', expand=True, fill='x', padx=5)

    def finish_training(window):
        nonlocal selected_words
        global words_filepath
        global results_filepath
        training_window.quit()
        training_window.destroy()
        # 更新原始单词库的数据
        # for _, selected_row in selected_words.iterrows():
        #
        #     index = selected_row['#']
        #     words_df[selected_words.columns] = words_df[selected_words.columns].astype('object')
        #     words_df.loc[words_df['#'] == index, selected_words.columns] = selected_row

        id_column = '#'  # 用来标识数据的主键列
        comparison_columns = ['选中次数', '正确次数']

        # 遍历选中的行，查找并更新不同的数据
        for i, row in selected_words.iterrows():
            # 使用唯一标识匹配，即这里的 id_column
            unique_id = row[id_column]

            # 找到 full_data 中匹配的行
            full_data_row_index = words_df[words_df[id_column] == unique_id].index

            if not full_data_row_index.empty:
                full_data_row_index = full_data_row_index[0]
                full_data_row = words_df.loc[full_data_row_index]

                # 比较并更新“选中次数”和“正确次数”
                for col in comparison_columns:
                    if full_data_row[col] != row[col]:
                        words_df.at[full_data_row_index, col] = row[col]

        words_df.to_csv(words_filepath, index=False)
        save_training_results(selected_words, results_filepath, window)


    training_window = ttk.Toplevel(
        title="汪涵背单词V1.0 - Training",  # 设置窗口的标题
        size=(400, 300),  # 窗口的大小
        position=(1000, 500),  # 窗口所在的位置
        minsize=(400, 300),  # 窗口的最小宽高
        maxsize=(400, 300),  # 窗口的最大宽高

        alpha=1.0,  # 设置窗口的透明度(0.0完全透明）
    )
    training_window.iconbitmap('icon.ico')

    # 创建显示单词、释义及按钮的界面
    meaning_frame = ttk.Frame(training_window)
    meaning_frame.grid_propagate(False)
    meaning_frame.config(height=35)

    word_display = ttk.Label(training_window,
                             text=f"{selected_words.at[current_index, '单词']}",
                             font=("Arial", 24),
                             background='#222222',
                             foreground='#ffffff',
                             )
    meaning_label = ttk.Label(meaning_frame,
                              text="",
                              font=("Microsoft YahHei UI", 12),
                              background='#222222',
                              foreground='#ffffff',
                              wraplength=300,
                              )
    meaning_label.pack()


    ifo_label = ttk.Label(training_window,
                              text="",
                              font=("Arial", 8),
                              background='#222222',
                              foreground='#ffffff',
                              )




    # 设置固定高度。例如，200像素（根据窗口大小调整）。
    # 布局部件
    training_window.grid_columnconfigure(0, weight=1)

    ifo_label.grid(row=0, column=0, pady=(0, 10), sticky="n")
    word_display.grid(row=1, column=0, pady=40, sticky="n")
    meaning_frame.grid(row=2, column=0, sticky='sew')

    style1 = ttk.Style()
    style1.configure('MyFrame.TFrame', background='#ffffff')

    button_frame = ttk.Frame(training_window)



    button_frame.grid(row=3, column=0, pady=20, sticky='sew')  # 沿着底部扩展且对齐到底部



    training_window.grid_rowconfigure(3, weight=1)
    next_button = ttk.Button(button_frame, text="下一个", command=next_word, width=20)

    known_button = ttk.Button(button_frame, text="认识", command=lambda: acknowledge_word(True), width=20, bootstyle=SUCCESS)
    unknown_button = ttk.Button(button_frame, text="不认识", command=lambda: acknowledge_word(False), width=20, style=DANGER)

    # 使用pack使按钮相邻
    known_button.pack(side='left', expand=True, fill='x', padx=5)
    unknown_button.pack(side='right', expand=True, fill='x', padx=5)

    def on_training_close(window):
        finish_training(window)

    training_window.protocol("WM_DELETE_WINDOW", lambda:on_training_close(window))






# 定义一个函数用来在结束练习时保存练习结果
def save_training_results(results, results_filepath, window):

    # 保存DataFrame到CSV文件，不写入索引
    words_df.to_csv(results_filepath, index=False)

    # 追加到之前的练习结果中去，如果文件不存在则创建一个
    correct_count = results['正确次数'].sum()
    if current_index > 0:
        accuracy = know_count / current_index
    else:
        accuracy = 0.0

    def save():
        print("1")
        with open(results_filepath, 'a', newline='', encoding='utf-8') as file:
            file.seek(0, 2)  # 移动到文件末尾
            if file.tell() == 0:
                file.write('日期,练习单词数量,正确个数,准确率\n')
            # 写入本次练习的结果
            date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            file.write(f'{date_str},{current_index},{know_count},{accuracy:.2f}\n')
        window.destroy()

    result_window = ttk.Toplevel(window)
    result_window.title("汪涵背单词V1.0 - Result")  # 设置窗口的标题

    # 设置窗口大小
    result_window.geometry("400x300+1000+500")  # 窗口大小和位置

    # 设置窗口的最小和最大尺寸
    result_window.minsize(400, 300)
    result_window.maxsize(400, 300)

    # 设置窗口透明度
    result_window.attributes("-alpha", 1.0)  # 设置窗口的透明度

    # 创建并添加标签
    accuracy_label = ttk.Label(
        result_window,
        text="{:.2f}%".format(accuracy * 100),
        font=("Arial", 36),
        background='#222222',
        foreground='#ffffff',
    )

    save_botton = ttk.Button(result_window, text="保存并退出", command=lambda: save(), width=15, bootstyle=SUCCESS)
    blank_label = ttk.Label(result_window, text="", background='#222222',)
    blank_label.pack(pady=20)
    accuracy_label.pack(pady=40)
    save_botton.pack(pady=10)

    def on_toplevel_close():
        window.destroy()

    result_window.protocol("WM_DELETE_WINDOW", on_toplevel_close)
    window.mainloop()

# 运行程序
if __name__ == "__main__":
    words_filepath = "All.csv"
    results_filepath = "result.csv"

    words_df = load_words(words_filepath)

    # 开始设置练习
    win = setup_training(words_df)


