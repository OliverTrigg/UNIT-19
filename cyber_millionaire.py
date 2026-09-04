import tkinter as tk
from tkinter import messagebox
import random


class CyberMillionaire:
    def __init__(self, root):
        self.root = root
        self.root.title("Cybersecurity Millionaire")
        self.root.geometry("1250x780")
        self.root.configure(bg="#050b18")
        self.root.resizable(False, False)

        # ==========================================================
        # COLOURS
        # ==========================================================

        self.bg = "#050b18"
        self.panel = "#0b1528"
        self.panel2 = "#132442"
        self.blue = "#087cff"
        self.blue_dark = "#0754a8"
        self.gold = "#ffd700"
        self.white = "#ffffff"
        self.grey = "#8fa3bd"
        self.green = "#00d26a"
        self.red = "#ff3b55"
        self.orange = "#ff9f1c"
        self.purple = "#8b5cf6"

        # ==========================================================
        # MONEY LADDER
        # ==========================================================

        self.money = [
            100,
            200,
            300,
            500,
            1000,
            2000,
            4000,
            8000,
            16000,
            32000,
            64000,
            125000,
            250000,
            500000,
            1000000
        ]

        # ONLY these questions are checkpoints.
        # Cash out is ONLY available here.
        self.checkpoints = {
            5: 1000,
            10: 32000
        }

        # ==========================================================
        # QUESTIONS
        # ==========================================================

        self.questions = {

            "easy": [
                (
                    "What does the 'S' in HTTPS stand for?",
                    ["Secure", "System", "Server", "Software"],
                    "Secure"
                ),
                (
                    "Which of these is the strongest password?",
                    [
                        "password123",
                        "qwerty",
                        "Blue!Tiger92#Moon",
                        "12345678"
                    ],
                    "Blue!Tiger92#Moon"
                ),
                (
                    "What is phishing?",
                    [
                        "A type of computer hardware",
                        "A scam designed to steal information",
                        "A programming language",
                        "A type of firewall"
                    ],
                    "A scam designed to steal information"
                ),
                (
                    "What should you do with a suspicious email attachment?",
                    [
                        "Open it immediately",
                        "Forward it to friends",
                        "Verify the sender before opening it",
                        "Rename the file"
                    ],
                    "Verify the sender before opening it"
                ),
                (
                    "Which of these is malware?",
                    [
                        "Firewall",
                        "Trojan",
                        "Password manager",
                        "VPN"
                    ],
                    "Trojan"
                ),
                (
                    "What is a firewall mainly used for?",
                    [
                        "Cooling a computer",
                        "Filtering network traffic",
                        "Creating passwords",
                        "Backing up files"
                    ],
                    "Filtering network traffic"
                ),
                (
                    "What does MFA stand for?",
                    [
                        "Multiple File Access",
                        "Multi-Factor Authentication",
                        "Managed Firewall Access",
                        "Main Function Authentication"
                    ],
                    "Multi-Factor Authentication"
                ),
                (
                    "Which is safest when using public Wi-Fi?",
                    [
                        "Accessing banking without protection",
                        "Using a trusted VPN",
                        "Sharing files with strangers",
                        "Disabling security settings"
                    ],
                    "Using a trusted VPN"
                ),
                (
                    "What is a computer virus?",
                    [
                        "A physical computer component",
                        "Malicious software that can replicate",
                        "A firewall",
                        "An encryption algorithm"
                    ],
                    "Malicious software that can replicate"
                ),
                (
                    "Why are software updates important?",
                    [
                        "They always make computers faster",
                        "They can fix security vulnerabilities",
                        "They remove the internet",
                        "They delete passwords"
                    ],
                    "They can fix security vulnerabilities"
                ),
                (
                    "Which should you avoid sharing publicly?",
                    [
                        "Your favourite colour",
                        "Your home address",
                        "Your favourite film",
                        "Your favourite music"
                    ],
                    "Your home address"
                ),
                (
                    "What is encryption?",
                    [
                        "Deleting data",
                        "Converting data into a protected form",
                        "Speeding up a network",
                        "Scanning a keyboard"
                    ],
                    "Converting data into a protected form"
                ),
                (
                    "Which device connects multiple devices on a local network?",
                    [
                        "Switch",
                        "Monitor",
                        "Keyboard",
                        "Printer"
                    ],
                    "Switch"
                ),
                (
                    "What is a backup?",
                    [
                        "A separate copy of data",
                        "A type of malware",
                        "A password attack",
                        "A firewall rule"
                    ],
                    "A separate copy of data"
                ),
                (
                    "Which is an example of biometric authentication?",
                    [
                        "Password",
                        "PIN",
                        "Fingerprint",
                        "Username"
                    ],
                    "Fingerprint"
                )
            ],

            "medium": [
                (
                    "What type of attack overwhelms a service with traffic?",
                    [
                        "DDoS",
                        "Phishing",
                        "SQL Injection",
                        "Brute Force"
                    ],
                    "DDoS"
                ),
                (
                    "What does SQL injection target?",
                    [
                        "Database queries",
                        "Graphics cards",
                        "Wi-Fi signals",
                        "Operating system updates"
                    ],
                    "Database queries"
                ),
                (
                    "What is the principle of least privilege?",
                    [
                        "Everyone gets administrator access",
                        "Users receive only the access they need",
                        "Passwords should be short",
                        "Systems need no authentication"
                    ],
                    "Users receive only the access they need"
                ),
                (
                    "What does DNS primarily do?",
                    [
                        "Encrypt hard drives",
                        "Translate domain names to IP addresses",
                        "Scan for viruses",
                        "Create user accounts"
                    ],
                    "Translate domain names to IP addresses"
                ),
                (
                    "Which attack repeatedly guesses passwords?",
                    [
                        "Brute-force attack",
                        "DDoS attack",
                        "Man-in-the-middle attack",
                        "Watering-hole attack"
                    ],
                    "Brute-force attack"
                ),
                (
                    "What is a man-in-the-middle attack?",
                    [
                        "An attacker intercepts communication",
                        "An attacker destroys a hard drive",
                        "A password is automatically changed",
                        "A firewall blocks traffic"
                    ],
                    "An attacker intercepts communication"
                ),
                (
                    "What is a hash commonly used for?",
                    [
                        "Representing passwords in a one-way form",
                        "Increasing monitor brightness",
                        "Connecting keyboards",
                        "Compressing video"
                    ],
                    "Representing passwords in a one-way form"
                ),
                (
                    "What is a salt in password security?",
                    [
                        "Random data added before hashing",
                        "A firewall rule",
                        "A network cable",
                        "An antivirus program"
                    ],
                    "Random data added before hashing"
                ),
                (
                    "Which protocol is commonly used for secure remote administration?",
                    [
                        "SSH",
                        "FTP",
                        "HTTP",
                        "Telnet"
                    ],
                    "SSH"
                ),
                (
                    "What is ransomware?",
                    [
                        "Malware that encrypts data and demands payment",
                        "A password manager",
                        "A firewall",
                        "A backup system"
                    ],
                    "Malware that encrypts data and demands payment"
                ),
                (
                    "What is a zero-day vulnerability?",
                    [
                        "A vulnerability without an available patch when exploited",
                        "A vulnerability lasting one day",
                        "An expired password",
                        "A deleted account"
                    ],
                    "A vulnerability without an available patch when exploited"
                ),
                (
                    "What does the CIA triad represent?",
                    [
                        "Confidentiality, Integrity, Availability",
                        "Control, Internet, Authentication",
                        "Cybersecurity, Intelligence, Access",
                        "Confidentiality, Internet, Authentication"
                    ],
                    "Confidentiality, Integrity, Availability"
                ),
                (
                    "What is network segmentation used for?",
                    [
                        "Limiting the spread of attacks",
                        "Making passwords shorter",
                        "Removing authentication",
                        "Increasing screen resolution"
                    ],
                    "Limiting the spread of attacks"
                ),
                (
                    "What is social engineering?",
                    [
                        "Manipulating people into revealing information",
                        "Designing social media websites",
                        "Building network cables",
                        "Encrypting databases"
                    ],
                    "Manipulating people into revealing information"
                ),
                (
                    "What is an IDS?",
                    [
                        "Intrusion Detection System",
                        "Internet Data Server",
                        "Identity Distribution Service",
                        "Internal Domain Security"
                    ],
                    "Intrusion Detection System"
                )
            ],

            "hard": [
                (
                    "Which property prevents someone denying they performed an action?",
                    [
                        "Non-repudiation",
                        "Availability",
                        "Obfuscation",
                        "Compression"
                    ],
                    "Non-repudiation"
                ),
                (
                    "What is the primary purpose of a digital signature?",
                    [
                        "Prove authenticity and integrity",
                        "Hide an IP address",
                        "Increase bandwidth",
                        "Create a firewall"
                    ],
                    "Prove authenticity and integrity"
                ),
                (
                    "What is a CSRF attack?",
                    [
                        "Tricking an authenticated user into sending an unwanted request",
                        "Cracking an encrypted hard drive",
                        "Flooding a network",
                        "Guessing passwords"
                    ],
                    "Tricking an authenticated user into sending an unwanted request"
                ),
                (
                    "Which HTTP status code commonly means Forbidden?",
                    ["200", "301", "403", "500"],
                    "403"
                ),
                (
                    "What does XSS stand for?",
                    [
                        "Cross-Site Scripting",
                        "Extended Security System",
                        "Cross Server Security",
                        "External Script Service"
                    ],
                    "Cross-Site Scripting"
                ),
                (
                    "What is privilege escalation?",
                    [
                        "Gaining higher permissions than authorised",
                        "Changing a password",
                        "Installing antivirus",
                        "Creating a backup"
                    ],
                    "Gaining higher permissions than authorised"
                ),
                (
                    "Which technique helps defend against SQL injection?",
                    [
                        "Parameterized queries",
                        "Disabling backups",
                        "Using shorter passwords",
                        "Allowing raw input in queries"
                    ],
                    "Parameterized queries"
                ),
                (
                    "What is a supply-chain attack?",
                    [
                        "Compromising a trusted supplier or dependency",
                        "Attacking a warehouse",
                        "Stealing cables",
                        "Blocking an internet connection"
                    ],
                    "Compromising a trusted supplier or dependency"
                ),
                (
                    "What does EDR stand for?",
                    [
                        "Endpoint Detection and Response",
                        "Encrypted Data Router",
                        "External Domain Registry",
                        "Endpoint Data Recovery"
                    ],
                    "Endpoint Detection and Response"
                ),
                (
                    "What is lateral movement?",
                    [
                        "Moving through systems after gaining an initial foothold",
                        "Moving a server physically",
                        "Changing a password",
                        "Updating antivirus"
                    ],
                    "Moving through systems after gaining an initial foothold"
                ),
                (
                    "What is a race condition?",
                    [
                        "A flaw caused by unexpected timing between operations",
                        "A password attack",
                        "A network scanning tool",
                        "A type of malware"
                    ],
                    "A flaw caused by unexpected timing between operations"
                ),
                (
                    "What does PKI stand for?",
                    [
                        "Public Key Infrastructure",
                        "Private Key Internet",
                        "Protected Kernel Interface",
                        "Public Knowledge Index"
                    ],
                    "Public Key Infrastructure"
                ),
                (
                    "Which technology can be used for secure key exchange?",
                    [
                        "Diffie-Hellman",
                        "MD5",
                        "FTP",
                        "Telnet"
                    ],
                    "Diffie-Hellman"
                ),
                (
                    "What is an air-gapped system?",
                    [
                        "A system isolated from unsecured networks",
                        "A cloud server",
                        "A wireless router",
                        "A system with no encryption"
                    ],
                    "A system isolated from unsecured networks"
                ),
                (
                    "What is the purpose of a SIEM?",
                    [
                        "Collecting and analysing security events",
                        "Encrypting every file",
                        "Replacing all firewalls",
                        "Generating passwords only"
                    ],
                    "Collecting and analysing security events"
                )
            ]
        }

        # ==========================================================
        # GAME STATE
        # ==========================================================

        self.difficulty = None
        self.game_questions = []
        self.current_question = 0

        self.guaranteed_winnings = 0

        self.used_5050 = False
        self.used_phone = False
        self.used_audience = False

        self.answer_buttons = []
        self.answer_locked = False

        self.show_start()

    # ==========================================================
    # CLEAR SCREEN
    # ==========================================================

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ==========================================================
    # BUTTON CREATOR
    # ==========================================================

    def make_button(
        self,
        parent,
        text,
        command,
        width=20,
        bg=None,
        fg=None
    ):
        if bg is None:
            bg = self.panel

        if fg is None:
            fg = self.white

        return tk.Button(
            parent,
            text=text,
            command=command,
            width=width,
            height=2,
            bg=bg,
            fg=fg,
            activebackground=self.blue,
            activeforeground=self.white,
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2"
        )

    # ==========================================================
    # START SCREEN
    # ==========================================================

    def show_start(self):
        self.clear()

        frame = tk.Frame(self.root, bg=self.bg)
        frame.pack(expand=True)

        tk.Label(
            frame,
            text="CYBERSECURITY",
            font=("Segoe UI", 28, "bold"),
            fg=self.blue,
            bg=self.bg
        ).pack()

        tk.Label(
            frame,
            text="MILLIONAIRE",
            font=("Segoe UI", 52, "bold"),
            fg=self.white,
            bg=self.bg
        ).pack()

        tk.Label(
            frame,
            text="The ultimate cybersecurity quiz",
            font=("Segoe UI", 15),
            fg=self.grey,
            bg=self.bg
        ).pack(pady=10)

        tk.Label(
            frame,
            text="15 questions • 3 lifelines • £1,000,000 top prize",
            font=("Segoe UI", 12),
            fg=self.grey,
            bg=self.bg
        ).pack()

        self.make_button(
            frame,
            "START GAME",
            self.choose_difficulty,
            width=28,
            bg=self.blue
        ).pack(pady=35)

    # ==========================================================
    # DIFFICULTY
    # ==========================================================

    def choose_difficulty(self):
        self.clear()

        frame = tk.Frame(self.root, bg=self.bg)
        frame.pack(expand=True)

        tk.Label(
            frame,
            text="SELECT DIFFICULTY",
            font=("Segoe UI", 30, "bold"),
            fg=self.white,
            bg=self.bg
        ).pack(pady=30)

        tk.Label(
            frame,
            text="The difficulty determines the question pool.",
            font=("Segoe UI", 12),
            fg=self.grey,
            bg=self.bg
        ).pack(pady=5)

        self.make_button(
            frame,
            "EASY",
            lambda: self.begin("easy"),
            width=28,
            bg=self.green,
            fg=self.bg
        ).pack(pady=10)

        self.make_button(
            frame,
            "MEDIUM",
            lambda: self.begin("medium"),
            width=28,
            bg=self.orange,
            fg=self.bg
        ).pack(pady=10)

        self.make_button(
            frame,
            "HARD",
            lambda: self.begin("hard"),
            width=28,
            bg=self.red,
            fg=self.white
        ).pack(pady=10)

    # ==========================================================
    # BEGIN GAME
    # ==========================================================

    def begin(self, difficulty):

        self.difficulty = difficulty

        self.game_questions = self.questions[difficulty].copy()

        random.shuffle(self.game_questions)

        self.current_question = 0

        self.guaranteed_winnings = 0

        self.used_5050 = False
        self.used_phone = False
        self.used_audience = False

        self.show_question()

    # ==========================================================
    # QUESTION SCREEN
    # ==========================================================

    def show_question(self):

        self.clear()

        self.answer_locked = False
        self.answer_buttons = []

        question_number = self.current_question + 1

        question, answers, correct = self.game_questions[
            self.current_question
        ]

        shuffled_answers = answers.copy()
        random.shuffle(shuffled_answers)

        # ======================================================
        # MAIN CONTAINER
        # ======================================================

        main = tk.Frame(self.root, bg=self.bg)
        main.pack(fill="both", expand=True)

        left = tk.Frame(main, bg=self.bg)
        left.pack(side="left", fill="both", expand=True)

        right = tk.Frame(
            main,
            bg=self.panel,
            width=245
        )
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        # ======================================================
        # TITLE
        # ======================================================

        tk.Label(
            left,
            text="CYBERSECURITY MILLIONAIRE",
            font=("Segoe UI", 22, "bold"),
            fg=self.blue,
            bg=self.bg
        ).pack(pady=(20, 2))

        tk.Label(
            left,
            text=f"QUESTION {question_number} / 15",
            font=("Segoe UI", 11, "bold"),
            fg=self.grey,
            bg=self.bg
        ).pack(pady=(0, 15))

        # ======================================================
        # QUESTION BOX
        # ======================================================

        qbox = tk.Frame(
            left,
            bg=self.panel,
            height=145
        )
        qbox.pack(fill="x", padx=35)
        qbox.pack_propagate(False)

        tk.Label(
            qbox,
            text=question,
            font=("Segoe UI", 17, "bold"),
            fg=self.white,
            bg=self.panel,
            wraplength=780,
            justify="center"
        ).pack(expand=True)

        # ======================================================
        # ANSWER BUTTONS
        # ======================================================

        answers_frame = tk.Frame(left, bg=self.bg)
        answers_frame.pack(pady=20)

        for i, answer in enumerate(shuffled_answers):

            letter = chr(65 + i)

            button = tk.Button(
                answers_frame,
                text=f"{letter}: {answer}",
                command=lambda a=answer: self.answer(a),
                width=39,
                height=2,
                bg=self.panel2,
                fg=self.white,
                activebackground=self.blue,
                activeforeground=self.white,
                font=("Segoe UI", 10, "bold"),
                relief="flat",
                bd=0,
                cursor="hand2"
            )

            button.grid(
                row=i // 2,
                column=i % 2,
                padx=6,
                pady=6
            )

            self.answer_buttons.append(button)

        # ======================================================
        # LIFELINES
        # ======================================================

        lifeline_frame = tk.Frame(left, bg=self.bg)
        lifeline_frame.pack(pady=5)

        self.lifeline_5050 = self.make_button(
            lifeline_frame,
            "50 / 50",
            self.use_5050,
            width=13
        )
        self.lifeline_5050.grid(row=0, column=0, padx=4)

        self.lifeline_phone = self.make_button(
            lifeline_frame,
            "PHONE A FRIEND",
            self.phone_friend,
            width=16
        )
        self.lifeline_phone.grid(row=0, column=1, padx=4)

        self.lifeline_audience = self.make_button(
            lifeline_frame,
            "ASK AUDIENCE",
            self.ask_audience,
            width=16
        )
        self.lifeline_audience.grid(row=0, column=2, padx=4)

        # ======================================================
        # CASH-OUT AREA
        #
        # VERY IMPORTANT:
        #
        # THERE IS NO CASH-OUT BUTTON HERE.
        #
        # The normal question screen cannot cash out.
        # ======================================================

        tk.Label(
            left,
            text="Cash out is available ONLY when you reach a checkpoint.",
            font=("Segoe UI", 10),
            fg="#53677f",
            bg=self.bg
        ).pack(pady=8)

        # ======================================================
        # MONEY LADDER
        # ======================================================

        tk.Label(
            right,
            text="MONEY LADDER",
            font=("Segoe UI", 15, "bold"),
            fg=self.gold,
            bg=self.panel
        ).pack(pady=15)

        for i in range(14, -1, -1):

            amount = self.money[i]

            if i == self.current_question:
                background = self.gold
                foreground = self.bg

            elif i < self.current_question:
                background = "#172438"
                foreground = "#64758a"

            else:
                background = self.panel
                foreground = self.white

            checkpoint_marker = ""

            if i + 1 in self.checkpoints:
                checkpoint_marker = " ★"

            tk.Label(
                right,
                text=f"£{amount:,}{checkpoint_marker}",
                font=("Segoe UI", 10, "bold"),
                bg=background,
                fg=foreground,
                width=21,
                pady=4
            ).pack(pady=1)

    # ==========================================================
    # ANSWER SELECTED
    # ==========================================================

    def answer(self, selected):

        if self.answer_locked:
            return

        self.answer_locked = True

        for button in self.answer_buttons:
            button.config(state="disabled")

        for button in self.answer_buttons:
            if selected in button.cget("text"):
                button.config(bg=self.blue)

        # 2 second delay
        self.root.after(
            2000,
            lambda: self.reveal(selected)
        )

    # ==========================================================
    # REVEAL ANSWER
    # ==========================================================

    def reveal(self, selected):

        question, answers, correct = self.game_questions[
            self.current_question
        ]

        # ------------------------------------------------------
        # CORRECT
        # ------------------------------------------------------

        if selected == correct:

            for button in self.answer_buttons:
                if correct in button.cget("text"):
                    button.config(
                        bg=self.green,
                        fg=self.bg
                    )

            question_number = self.current_question + 1

            # --------------------------------------------------
            # CHECKPOINT
            # --------------------------------------------------

            if question_number in self.checkpoints:

                checkpoint_amount = self.checkpoints[
                    question_number
                ]

                self.guaranteed_winnings = checkpoint_amount

                self.root.after(
                    1500,
                    lambda: self.show_checkpoint(
                        checkpoint_amount
                    )
                )

            else:

                self.root.after(
                    1500,
                    self.next_question
                )

        # ------------------------------------------------------
        # WRONG
        # ------------------------------------------------------

        else:

            for button in self.answer_buttons:

                text = button.cget("text")

                if correct in text:
                    button.config(
                        bg=self.green,
                        fg=self.bg
                    )

                elif selected in text:
                    button.config(
                        bg=self.red,
                        fg=self.white
                    )

            self.root.after(
                1800,
                self.game_over
            )

    # ==========================================================
    # CHECKPOINT SCREEN
    # ==========================================================

    def show_checkpoint(self, amount):

        self.clear()

        frame = tk.Frame(self.root, bg=self.bg)
        frame.pack(expand=True)

        tk.Label(
            frame,
            text="★ CHECKPOINT ★",
            font=("Segoe UI", 36, "bold"),
            fg=self.gold,
            bg=self.bg
        ).pack(pady=25)

        tk.Label(
            frame,
            text="CONGRATULATIONS!",
            font=("Segoe UI", 20, "bold"),
            fg=self.white,
            bg=self.bg
        ).pack()

        tk.Label(
            frame,
            text="You have secured",
            font=("Segoe UI", 15),
            fg=self.grey,
            bg=self.bg
        ).pack(pady=(25, 0))

        tk.Label(
            frame,
            text=f"£{amount:,}",
            font=("Segoe UI", 60, "bold"),
            fg=self.gold,
            bg=self.bg
        ).pack()

        tk.Label(
            frame,
            text=(
                "You have reached a guaranteed checkpoint.\n"
                "You may now cash out or continue."
            ),
            font=("Segoe UI", 13),
            fg=self.grey,
            bg=self.bg,
            justify="center"
        ).pack(pady=20)

        # ======================================================
        # THE ONLY CASH OUT BUTTON
        #
        # This button is created ONLY by show_checkpoint().
        # ======================================================

        self.make_button(
            frame,
            f"CASH OUT £{amount:,}",
            lambda: self.cash_out(amount),
            width=30,
            bg=self.gold,
            fg=self.bg
        ).pack(pady=8)

        # ======================================================
        # CONTINUE
        # ======================================================

        self.make_button(
            frame,
            "CONTINUE PLAYING",
            self.next_question,
            width=30,
            bg=self.blue,
            fg=self.white
        ).pack(pady=8)

    # ==========================================================
    # CASH OUT
    # ==========================================================

    def cash_out(self, amount):

        # ======================================================
        # HARD CHECK
        #
        # Cash out is only valid on Q5 or Q10.
        # ======================================================

        question_number = self.current_question + 1

        if question_number not in self.checkpoints:
            return

        if amount != self.checkpoints[question_number]:
            return

        if self.guaranteed_winnings != amount:
            return

        confirmed = messagebox.askyesno(
            "Confirm Cash Out",
            f"Are you sure you want to cash out £{amount:,}?"
        )

        if confirmed:

            self.show_end(
                "YOU CASHED OUT!",
                amount,
                self.gold
            )

    # ==========================================================
    # NEXT QUESTION
    # ==========================================================

    def next_question(self):

        self.current_question += 1

        if self.current_question >= 15:
            self.win()
        else:
            self.show_question()

    # ==========================================================
    # 50 / 50
    # ==========================================================

    def use_5050(self):

        if self.used_5050:
            return

        self.used_5050 = True

        self.lifeline_5050.config(
            state="disabled",
            bg="#273547"
        )

        question, answers, correct = self.game_questions[
            self.current_question
        ]

        wrong_buttons = []

        for button in self.answer_buttons:

            if correct not in button.cget("text"):
                wrong_buttons.append(button)

        random.shuffle(wrong_buttons)

        for button in wrong_buttons[:2]:
            button.config(
                text="",
                state="disabled",
                bg="#060d18"
            )

    # ==========================================================
    # PHONE A FRIEND
    # ==========================================================

    def phone_friend(self):

        if self.used_phone:
            return

        self.used_phone = True

        self.lifeline_phone.config(
            state="disabled",
            bg="#273547"
        )

        question, answers, correct = self.game_questions[
            self.current_question
        ]

        confidence = random.randint(65, 95)

        messagebox.showinfo(
            "Phone a Friend",
            (
                "Your friend has been contacted.\n\n"
                f"They think the answer is:\n\n"
                f"{correct}\n\n"
                f"Confidence: {confidence}%"
            )
        )

    # ==========================================================
    # ASK AUDIENCE
    # ==========================================================

    def ask_audience(self):

        if self.used_audience:
            return

        self.used_audience = True

        self.lifeline_audience.config(
            state="disabled",
            bg="#273547"
        )

        question, answers, correct = self.game_questions[
            self.current_question
        ]

        correct_percentage = random.randint(55, 80)

        remaining = 100 - correct_percentage

        incorrect = [
            a for a in answers if a != correct
        ]

        percentages = {
            correct: correct_percentage
        }

        random_parts = []

        for _ in range(len(incorrect) - 1):
            if remaining > 0:
                value = random.randint(
                    0,
                    remaining
                )
            else:
                value = 0

            random_parts.append(value)
            remaining -= value

        random_parts.append(remaining)

        for answer, percentage in zip(
            incorrect,
            random_parts
        ):
            percentages[answer] = percentage

        result = "AUDIENCE RESULTS\n\n"

        for answer in answers:
            result += (
                f"{answer}: "
                f"{percentages[answer]}%\n"
            )

        messagebox.showinfo(
            "Ask the Audience",
            result
        )

    # ==========================================================
    # GAME OVER
    # ==========================================================

    def game_over(self):

        self.show_end(
            "GAME OVER",
            self.guaranteed_winnings,
            self.red
        )

    # ==========================================================
    # WIN
    # ==========================================================

    def win(self):

        self.show_end(
            "YOU ARE A CYBER MILLIONAIRE!",
            1000000,
            self.gold
        )

    # ==========================================================
    # END SCREEN
    # ==========================================================

    def show_end(
        self,
        title,
        winnings,
        colour
    ):

        self.clear()

        frame = tk.Frame(
            self.root,
            bg=self.bg
        )
        frame.pack(expand=True)

        tk.Label(
            frame,
            text=title,
            font=("Segoe UI", 31, "bold"),
            fg=colour,
            bg=self.bg,
            wraplength=900
        ).pack(pady=30)

        tk.Label(
            frame,
            text="FINAL WINNINGS",
            font=("Segoe UI", 14, "bold"),
            fg=self.grey,
            bg=self.bg
        ).pack()

        tk.Label(
            frame,
            text=f"£{winnings:,}",
            font=("Segoe UI", 60, "bold"),
            fg=self.gold,
            bg=self.bg
        ).pack(pady=15)

        if winnings == 1000000:

            text = (
                "Amazing! You answered all 15 "
                "cybersecurity questions correctly."
            )

        elif winnings >= 32000:

            text = (
                "Excellent result! You reached "
                "the £32,000 checkpoint."
            )

        elif winnings >= 1000:

            text = (
                "Well done! You reached "
                "the £1,000 checkpoint."
            )

        else:

            text = (
                "Keep learning cybersecurity "
                "and try again!"
            )

        tk.Label(
            frame,
            text=text,
            font=("Segoe UI", 14),
            fg=self.grey,
            bg=self.bg
        ).pack(pady=15)

        self.make_button(
            frame,
            "PLAY AGAIN",
            self.choose_difficulty,
            width=25,
            bg=self.blue
        ).pack(pady=12)

        self.make_button(
            frame,
            "MAIN MENU",
            self.show_start,
            width=25
        ).pack(pady=5)


# ==============================================================
# RUN GAME
# ==============================================================

if __name__ == "__main__":

    root = tk.Tk()

    game = CyberMillionaire(root)

    root.mainloop()
