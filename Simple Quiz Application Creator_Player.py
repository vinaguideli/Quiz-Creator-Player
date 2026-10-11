import json #json saves and loads quizzes
import os #os handles file names
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

MIN_OPTIONS = 2
MAX_OPTIONS = 6
DEFAULT_OPTIONS = 4

# using chat GPT ill add the colour combination 
BG            = "#F5F7FB"   
CARD          = "#FFFFFF"   
HEADER        = "#1E1B4B"   
PRIMARY       = "#4F46E5"   
PRIMARY_HOVER = "#4338CA"
PRIMARY_PRESS = "#3730A3"
PRIMARY_LIGHT = "#E0E7FF"   
TEXT          = "#1F2937"   
MUTED         = "#6B7280"   
BORDER        = "#D1D5DB"
SECONDARY     = "#E5E7EB"   
SECONDARY_HOV = "#D1D5DB"
DANGER        = "#DC2626"
DANGER_HOVER  = "#B91C1C"
SUCCESS       = "#15803D"
SUCCESS_BG    = "#DCFCE7"
ERROR         = "#B91C1C"
ERROR_BG      = "#FEE2E2"

FONT = ("Segoe UI", 10)


def setup_styles(root):
    """Configure one global ttk theme for the whole app."""
    s = ttk.Style(root)
    s.theme_use("clam")

    s.configure(".", background=BG, foreground=TEXT, font=FONT)

    # Frames
    s.configure("TFrame", background=BG)
    s.configure("Card.TFrame", background=CARD)
    s.configure("Header.TFrame", background=HEADER)

    # Labels
    s.configure("TLabel", background=BG, foreground=TEXT)
    s.configure("Card.TLabel", background=CARD, foreground=TEXT)
    s.configure("Muted.TLabel", background=BG, foreground=MUTED)
    s.configure("Header.TLabel", background=HEADER, foreground="#FFFFFF")
    s.configure("HeaderSub.TLabel", background=HEADER, foreground="#C7D2FE")

    # Buttons
    s.configure("TButton", background=PRIMARY, foreground="#FFFFFF",
                padding=(14, 7), borderwidth=0, focuscolor=PRIMARY,
                font=("Segoe UI", 10, "bold"))
    s.map("TButton",
          background=[("pressed", PRIMARY_PRESS), ("active", PRIMARY_HOVER)],
          foreground=[("disabled", "#9CA3AF")])

    s.configure("Secondary.TButton", background=SECONDARY, foreground=TEXT,
                focuscolor=SECONDARY)
    s.map("Secondary.TButton",
          background=[("pressed", BORDER), ("active", SECONDARY_HOV)])

    s.configure("Danger.TButton", background=DANGER, foreground="#FFFFFF",
                focuscolor=DANGER)
    s.map("Danger.TButton",
          background=[("pressed", "#991B1B"), ("active", DANGER_HOVER)])

    # Entry
    s.configure("TEntry", fieldbackground=CARD, foreground=TEXT,
                bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER,
                padding=5)
    s.map("TEntry",
          bordercolor=[("focus", PRIMARY)],
          lightcolor=[("focus", PRIMARY)],
          darkcolor=[("focus", PRIMARY)],
          fieldbackground=[("readonly", "#EEF0F6")])

    # Radiobuttons (page background + card background variants)
    s.configure("TRadiobutton", background=BG, foreground=TEXT,indicatorcolor=CARD, focuscolor=BG)
    s.map("TRadiobutton",indicatorcolor=[("selected", PRIMARY), ("active", PRIMARY_LIGHT)], background=[("active", PRIMARY_LIGHT)])

    s.configure("Card.TRadiobutton", background=CARD, foreground=TEXT,
                indicatorcolor=CARD, focuscolor=CARD, padding=(6, 4))
    s.map("Card.TRadiobutton",indicatorcolor=[("selected", PRIMARY), ("active", PRIMARY_LIGHT)],background=[("active", PRIMARY_LIGHT)])

    # Scrollbar / separator
    s.configure("Vertical.TScrollbar", background=BORDER, troughcolor=BG, bordercolor=BG, arrowcolor=MUTED, lightcolor=BORDER,darkcolor=BORDER)
    s.map("Vertical.TScrollbar", background=[("active", MUTED)])
    s.configure("TSeparator", background=BORDER)


def style_text_widget(w):
    w.configure(bg=CARD, fg=TEXT, insertbackground=TEXT, relief="flat",highlightthickness=1,
                highlightbackground=BORDER,highlightcolor=PRIMARY, font=FONT, padx=6, pady=6)


class Quiz:
    def __init__(self, title="Untitled Quiz"):
        self.title = title
        self.questions = []
        self.file_path = None

    def to_dict(self):
        return {"title": self.title, "questions": self.questions}

    @classmethod
    def from_dict(cls, d):
        q = cls(title=d.get("title", "Untitled Quiz"))
        q.questions = d.get("questions", [])
        return q

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
        self.file_path = path

    @classmethod
    def load(cls, path):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        q = cls.from_dict(d)
        q.file_path = path
        return q

class QuestionFormWindow(tk.Toplevel):
    def __init__(self, master, on_saved, question=None):
        super().__init__(master)
        self.configure(bg=BG)
        self.on_saved = on_saved
        self.editing = question is not None

        self.title("Edit Question" if self.editing else "Add Question")
        self.resizable(False, False)
        self.grab_set()

        starting_options = question["options"] if question else [""] * DEFAULT_OPTIONS
        starting_correct = question["correct_index"] if question else 0

        pad = {"padx": 10, "pady": 6}
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Question:").grid(row=0, column=0, sticky="ne", **pad)
        self.question_text = tk.Text(frm, width=40, height=3, wrap="word")
        style_text_widget(self.question_text)
        self.question_text.grid(row=0, column=1, columnspan=2, **pad)
        if question:
            self.question_text.insert("1.0", question["text"])

        ttk.Label(frm, text="Options (select the correct one):",
                  font=("Segoe UI", 10, "bold")).grid(
            row=1, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 0)
        )

        self.correct_var = tk.IntVar(value=starting_correct)
        self.option_vars = []
        self.option_rows = []
        self.options_frame = ttk.Frame(frm)
        self.options_frame.grid(row=2, column=0, columnspan=3, sticky="w")

        for text in starting_options:
            self._add_option_row(text)

        btns = ttk.Frame(frm)
        btns.grid(row=3, column=0, columnspan=3, pady=(6, 0), sticky="w")
        ttk.Button(btns, text="+ Add Option", style="Secondary.TButton",
                   command=lambda: self._add_option_row("")).pack(side="left")
        ttk.Button(btns, text="- Remove Last Option", style="Secondary.TButton",
                   command=self._remove_last_option).pack(side="left", padx=6)

        action_frm = ttk.Frame(self)
        action_frm.pack(pady=(5, 10))
        ttk.Button(action_frm, text="Save", command=self.save).pack(side="left", padx=5)
        ttk.Button(action_frm, text="Cancel", style="Secondary.TButton",
                   command=self.destroy).pack(side="left", padx=5)

    def _add_option_row(self, text):
        if len(self.option_vars) >= MAX_OPTIONS:
            messagebox.showinfo("Limit Reached", f"Maximum {MAX_OPTIONS} options allowed.", parent=self)
            return
        row_index = len(self.option_vars)
        var = tk.StringVar(value=text)
        row = ttk.Frame(self.options_frame)
        row.grid(row=row_index, column=0, sticky="w", pady=2, padx=10)

        rb = ttk.Radiobutton(row, variable=self.correct_var, value=row_index)
        rb.pack(side="left")
        entry = ttk.Entry(row, textvariable=var, width=35)
        entry.pack(side="left", padx=5)

        self.option_vars.append(var)
        self.option_rows.append(row)

    def _remove_last_option(self):
        if len(self.option_vars) <= MIN_OPTIONS:
            messagebox.showinfo("Minimum Required", f"At least {MIN_OPTIONS} options are required.", parent=self)
            return
        self.option_rows[-1].destroy()
        self.option_rows.pop()
        self.option_vars.pop()
        if self.correct_var.get() >= len(self.option_vars):
            self.correct_var.set(len(self.option_vars) - 1)

    def save(self):
        text = self.question_text.get("1.0", "end").strip()
        options = [v.get().strip() for v in self.option_vars]

        if not text:
            messagebox.showerror("Validation Error", "Question text is required.", parent=self)
            return
        if any(not opt for opt in options):
            messagebox.showerror("Validation Error", "All options must have text.", parent=self)
            return
        if len(options) < MIN_OPTIONS:
            messagebox.showerror("Validation Error", f"At least {MIN_OPTIONS} options are required.", parent=self)
            return

        correct_index = self.correct_var.get()
        self.on_saved({"text": text, "options": options, "correct_index": correct_index})
        self.destroy()

class CreateQuizWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.configure(bg=BG)
        self.title("Create Quiz")
        self.geometry("560x480")
        self.quiz = Quiz()

        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")
        ttk.Label(top, text="Quiz Title:", font=("Segoe UI", 10, "bold")).pack(side="left")
        self.title_var = tk.StringVar(value=self.quiz.title)
        title_entry = ttk.Entry(top, textvariable=self.title_var, width=35)
        title_entry.pack(side="left", padx=5)
        title_entry.bind("<FocusOut>", self._sync_title)

        ttk.Label(self, text="Questions:", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10)
        list_frm = ttk.Frame(self)
        list_frm.pack(fill="both", expand=True, padx=10, pady=5)
        scrollbar = ttk.Scrollbar(list_frm, orient="vertical")
        self.listbox = tk.Listbox( list_frm, height=14, yscrollcommand=scrollbar.set,bg=CARD, fg=TEXT, font=FONT, relief="flat", activestyle="none",
            selectbackground=PRIMARY, selectforeground="#FFFFFF",highlightthickness=1, highlightbackground=BORDER, highlightcolor=PRIMARY,
        )
        scrollbar.config(command=self.listbox.yview)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        btn_frm = ttk.Frame(self, padding=10)
        btn_frm.pack(fill="x")
        ttk.Button(btn_frm, text="Add Question", command=self.add_question).pack(side="left", padx=3)
        ttk.Button(btn_frm, text="Edit Question", style="Secondary.TButton",command=self.edit_question).pack(side="left", padx=3)
        ttk.Button(btn_frm, text="Delete Question", style="Danger.TButton",command=self.delete_question).pack(side="left", padx=3)

        file_frm = ttk.Frame(self, padding=(10, 0, 10, 10))
        file_frm.pack(fill="x")
        ttk.Button(file_frm, text="Load Quiz...", style="Secondary.TButton",command=self.load_quiz).pack(side="left", padx=3)
        ttk.Button(file_frm, text="Save Quiz As...", command=self.save_quiz).pack(side="left", padx=3)
        ttk.Button(file_frm, text="Close", style="Secondary.TButton",command=self.destroy).pack(side="right", padx=3)

        self.refresh()

    def _sync_title(self, _event=None):
        self.quiz.title = self.title_var.get().strip() or "Untitled Quiz"

    def refresh(self):
        self.listbox.delete(0, "end")
        for i, q in enumerate(self.quiz.questions, start=1):
            self.listbox.insert("end", f"  {i}. {q['text'][:60]}")

    def selected_index(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showerror("No Selection", "Please select a question first.", parent=self)
            return None
        return sel[0]

    def add_question(self):
        def on_saved(q):
            self.quiz.questions.append(q)
            self.refresh()
        QuestionFormWindow(self, on_saved)

    def edit_question(self):
        idx = self.selected_index()
        if idx is None:
            return

        def on_saved(q):
            self.quiz.questions[idx] = q
            self.refresh()
        QuestionFormWindow(self, on_saved, question=self.quiz.questions[idx])

    def delete_question(self):
        idx = self.selected_index()
        if idx is None:
            return
        if messagebox.askyesno("Confirm Delete", "Delete this question?", parent=self):
            self.quiz.questions.pop(idx)
            self.refresh()

    def load_quiz(self):
        path = filedialog.askopenfilename(
            title="Open Quiz", filetypes=[("Quiz JSON files", "*.json"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            self.quiz = Quiz.load(path)
            self.title_var.set(self.quiz.title)
            self.refresh()
            messagebox.showinfo("Loaded", f"Loaded quiz from:\n{os.path.basename(path)}", parent=self)
        except Exception as exc:
            messagebox.showerror("Load Error", f"Could not load quiz:\n{exc}", parent=self)

    def save_quiz(self):
        self._sync_title()
        if not self.quiz.questions:
            messagebox.showerror("Nothing to Save", "Add at least one question before saving.", parent=self)
            return
        path = filedialog.asksaveasfilename(
            title="Save Quiz As",
            defaultextension=".json",
            filetypes=[("Quiz JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"{self.quiz.title.replace(' ', '_')}.json",
        )
        if not path:
            return
        try:
            self.quiz.save(path)
            messagebox.showinfo("Saved", f"Quiz saved to:\n{os.path.basename(path)}", parent=self)
        except Exception as exc:
            messagebox.showerror("Save Error", f"Could not save quiz:\n{exc}", parent=self)

class PlayQuizSetupWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.configure(bg=BG)
        self.title("Play Quiz - Setup")
        self.geometry("440x230")
        self.resizable(False, False)

        self.quiz_path = tk.StringVar()
        self.player_name = tk.StringVar()

        frm = ttk.Frame(self, padding=20)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Quiz File:").grid(row=0, column=0, sticky="w", pady=8)
        path_frm = ttk.Frame(frm)
        path_frm.grid(row=0, column=1, pady=8, sticky="w")
        ttk.Entry(path_frm, textvariable=self.quiz_path, width=26, state="readonly").pack(side="left")
        ttk.Button(path_frm, text="Browse...", style="Secondary.TButton", command=self.browse).pack(side="left", padx=5)

        ttk.Label(frm, text="Player Name:").grid(row=1, column=0, sticky="w", pady=8)
        ttk.Entry(frm, textvariable=self.player_name, width=30).grid(row=1, column=1, sticky="w", pady=8)

        ttk.Button(frm, text="Start Quiz", command=self.start_quiz).grid(row=2, column=1, sticky="w", pady=20)

    def browse(self):
        path = filedialog.askopenfilename(
            title="Select Quiz File", filetypes=[("Quiz JSON files", "*.json"), ("All files", "*.*")]
        )
        if path:
            self.quiz_path.set(path)

    def start_quiz(self):
        path = self.quiz_path.get().strip()
        name = self.player_name.get().strip()

        if not path:
            messagebox.showerror("Validation Error", "Please select a quiz file.", parent=self)
            return
        if not name:
            messagebox.showerror("Validation Error", "Please enter a player name.", parent=self)
            return

        try:
            quiz = Quiz.load(path)
        except Exception as exc:
            messagebox.showerror("Load Error", f"Could not load quiz:\n{exc}", parent=self)
            return

        if not quiz.questions:
            messagebox.showerror("Empty Quiz", "This quiz file has no questions.", parent=self)
            return

        self.destroy()
        PlayQuizWindow(self.master, quiz, name)

class PlayQuizWindow(tk.Toplevel):
    def __init__(self, master, quiz: Quiz, player_name: str):
        super().__init__(master)
        self.configure(bg=BG)
        self.quiz = quiz
        self.player_name = player_name
        self.current_index = 0
        self.score = 0
        self.answer_log = []

        self.title(f"Play Quiz - {quiz.title}")
        self.geometry("540x440")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.confirm_quit)

        self.progress_label = ttk.Label(self, style="Muted.TLabel", font=("Segoe UI", 9, "italic"))
        self.progress_label.pack(anchor="w", padx=15, pady=(15, 5))

        card = ttk.Frame(self, style="Card.TFrame", padding=15)
        card.pack(fill="x", padx=15)

        self.question_label = ttk.Label(
            card, text="", style="Card.TLabel", wraplength=470,
            font=("Segoe UI", 12, "bold"), justify="left"
        )
        self.question_label.pack(anchor="w", pady=(0, 12))

        self.selected_option = tk.StringVar(value="-1")
        self.options_frame = ttk.Frame(card, style="Card.TFrame")
        self.options_frame.pack(fill="x", padx=5)

        self.next_btn = ttk.Button(self, text="Next Question", command=self.next_question)
        self.next_btn.pack(pady=20)

        self.show_question()

    def show_question(self):
        q = self.quiz.questions[self.current_index]
        total = len(self.quiz.questions)
        self.progress_label.config(text=f"Question {self.current_index + 1} of {total}")
        self.question_label.config(text=q["text"])

        for child in self.options_frame.winfo_children():
            child.destroy()

        self.selected_option.set("-1")
        for i, opt in enumerate(q["options"]):
            ttk.Radiobutton(
                self.options_frame, text=opt, variable=self.selected_option,
                value=str(i), style="Card.TRadiobutton"
            ).pack(anchor="w", fill="x", pady=3)

        is_last = self.current_index == total - 1
        self.next_btn.config(text="Finish Quiz" if is_last else "Next Question")

    def next_question(self):
        choice = self.selected_option.get()
        if choice == "-1":
            messagebox.showerror("No Answer", "Please select an answer before continuing.", parent=self)
            return

        selected_index = int(choice)
        q = self.quiz.questions[self.current_index]
        correct_index = q["correct_index"]
        if selected_index == correct_index:
            self.score += 1
        self.answer_log.append((q, selected_index, correct_index))

        if self.current_index + 1 < len(self.quiz.questions):
            self.current_index += 1
            self.show_question()
        else:
            self.finish_quiz()

    def finish_quiz(self):
        self.destroy()
        QuizResultsWindow(self.master, self.quiz, self.player_name, self.score, self.answer_log)

    def confirm_quit(self):
        if messagebox.askyesno("Quit Quiz", "Quit now? Your progress will be lost.", parent=self):
            self.destroy()

class QuizResultsWindow(tk.Toplevel):
    def __init__(self, master, quiz: Quiz, player_name, score, answer_log):
        super().__init__(master)
        self.configure(bg=BG)
        self.title("Quiz Results")
        self.geometry("580x500")

        total = len(quiz.questions)
        pct = (score / total * 100) if total else 0

        header = ttk.Frame(self, style="Header.TFrame", padding=15)
        header.pack(fill="x")
        ttk.Label(header, text=f"Results for {player_name}", style="Header.TLabel",
                  font=("Segoe UI", 14, "bold")).pack(anchor="w")
        ttk.Label(header, text=f"Quiz: {quiz.title}", style="HeaderSub.TLabel",
                  font=("Segoe UI", 10)).pack(anchor="w")
        score_color = "#86EFAC" if pct >= 50 else "#FCA5A5"
        tk.Label(header, text=f"Score: {score} / {total}  ({pct:.0f}%)",
                 bg=HEADER, fg=score_color,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(8, 0))

        ttk.Label(self, text="Answer Review:", font=("Segoe UI", 10, "bold")).pack(
            anchor="w", padx=15, pady=(12, 0))

        review_frm = ttk.Frame(self)
        review_frm.pack(fill="both", expand=True, padx=10, pady=5)
        canvas = tk.Canvas(review_frm, borderwidth=0, highlightthickness=0, bg=BG)
        scrollbar = ttk.Scrollbar(review_frm, orient="vertical", command=canvas.yview)
        inner = ttk.Frame(canvas)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(win_id, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for i, (q, selected_index, correct_index) in enumerate(answer_log, start=1):
            is_correct = selected_index == correct_index
            fg = SUCCESS if is_correct else ERROR
            bg = SUCCESS_BG if is_correct else ERROR_BG

            
            row = tk.Frame(inner, bg=BG)
            row.pack(fill="x", pady=4, padx=(0, 6))
            tk.Frame(row, bg=fg, width=5).pack(side="left", fill="y")
            body = tk.Frame(row, bg=bg)
            body.pack(side="left", fill="both", expand=True)

            tk.Label(body, text=f"{i}. {q['text']}", bg=bg, fg=TEXT,
                     font=("Segoe UI", 10, "bold"), wraplength=480,
                     justify="left", anchor="w").pack(anchor="w", padx=10, pady=(8, 2))

            given_text = q["options"][selected_index]
            correct_text = q["options"][correct_index]
            status = "Correct" if is_correct else "Incorrect"
            detail = f"Your answer: {given_text}  -  {status}"
            if not is_correct:
                detail += f"\nCorrect answer: {correct_text}"
            tk.Label(body, text=detail, bg=bg, fg=fg, font=FONT,
                     wraplength=480, justify="left", anchor="w").pack(anchor="w", padx=10, pady=(0, 8))

        btn_frm = ttk.Frame(self, padding=10)
        btn_frm.pack(fill="x")
        ttk.Button(btn_frm, text="Play Another Quiz", command=self.play_again).pack(side="left", padx=5)
        ttk.Button(btn_frm, text="Close", style="Secondary.TButton",
                   command=self.destroy).pack(side="right", padx=5)

    def play_again(self):
        self.destroy()
        PlayQuizSetupWindow(self.master)

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        setup_styles(self)
        self.configure(bg=BG)
        self.title("Quiz Application")
        self.geometry("380x320")
        self.resizable(False, False)

        banner = ttk.Frame(self, style="Header.TFrame", padding=(0, 28, 0, 22))
        banner.pack(fill="x")
        ttk.Label(banner, text="Quiz Application", style="Header.TLabel",
                  font=("Segoe UI", 18, "bold")).pack()
        ttk.Label(banner, text="Main Menu", style="HeaderSub.TLabel",
                  font=("Segoe UI", 11)).pack(pady=(4, 0))

        ttk.Button(self, text="Create Quiz", width=25, command=self.open_create).pack(pady=(30, 8))
        ttk.Button(self, text="Play Quiz", width=25, command=self.open_play).pack(pady=8)
        ttk.Button(self, text="Exit", width=25, style="Secondary.TButton",
                   command=self.destroy).pack(pady=(18, 0))

    def open_create(self):
        CreateQuizWindow(self)

    def open_play(self):
        PlayQuizSetupWindow(self)


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
