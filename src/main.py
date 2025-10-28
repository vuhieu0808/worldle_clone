import customtkinter as ctk
from PIL import Image
import cairosvg
import io
import json
import random

from compute import get_distance_and_arrow

BACKGROUND_COLOR = "#1e1e1e"
TEXT_COLOR = "#ffffff"
COLOR_ERROR = "#ff4444"

FONT_SMALL = ("Arial", 18, "bold")
FONT_ERROR = ("Arial", 16, "bold")

COUNTRY_DATA_PATH = "./src/assets/country.json"
COUNTRY_IMAGE_PATH = "./src/assets/countries/"

# Set customtkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class GameApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Game Application")
        self.geometry("1920x1080")
        self.config(bg=BACKGROUND_COLOR)

        # Load assets
        self.countryData = {} # (countryCode, data) (data: [Country Name, Latitude, Longitude, Population, Area])
        self.countryNametoCode = {} # (countryName.lower(), countryCode)
        self.countryImages = {} # Cache for country SVG images (countryCode, SvgImage)
        self.load_assets()

        # Secret country for the current game
        self.secretCountry = None
        self.secretCountryData = None
        self.secretCountryImage = None

        # Main frames
        self.startScreen = None
        self.gameScreen = None
        self.endScreen = None
        self.howToPlayScreen = None

        self.entry = None
        self.listBoxGuessed = None # List box những nước đã đoán
        self.guessedCountries = [] # List of guessed country codes

        self.selectedIndex = -1
        self.textBoxFrame = None        
        self.textBoxSuggestions = None # List box suggest countries
        self.curSuggestions = []

        self.toastLabel = None  # Toast notification label

        self.show_start_screen()

    def load_assets(self):
        # Load country data from JSON
        with open(COUNTRY_DATA_PATH, "r") as f:
            data = json.load(f)

        for country in data:
            countryInfo = country.copy()
            key = (countryInfo.pop("Country Code")).lower()
            self.countryData[key] = countryInfo
            self.countryNametoCode[countryInfo["Country Name"].lower()] = key

    def clear_screen(self):
        for screen in [self.startScreen, self.gameScreen, self.endScreen, self.howToPlayScreen]:
            if screen is not None:
                screen.destroy()
                screen = None

    def show_toast(self, message):
        if self.toastLabel:
            self.toastLabel.destroy()

        self.toastLabel = ctk.CTkLabel(
            self,
            text=message,
            fg_color=COLOR_ERROR,
            text_color=TEXT_COLOR,
            font=FONT_ERROR,
            corner_radius=8,
            width=300,
            height=60
        )
        self.toastLabel.place(relx=0.5, rely=0.1, anchor="center")
        self.after(2000, lambda: self.toastLabel.destroy() if self.toastLabel else None)

    def trigger_error_toast(self, text):
        self.show_toast(f"{text}")

    # Show screen methods
    def show_start_screen(self):
        self.clear_screen()
        self.startScreen = ctk.CTkFrame(self, fg_color=BACKGROUND_COLOR)
        self.startScreen.pack(expand=True, fill="both")

        # Title
        title_label = ctk.CTkLabel(
            self.startScreen,
            text="🌍 WORLDLE GAME 🌍",
            font=("Arial", 48, "bold"),
            text_color="#60a5fa"
        )
        title_label.place(relx=0.5, rely=0.25, anchor="center")

        subtitle_label = ctk.CTkLabel(
            self.startScreen,
            text="Guess the Country!",
            font=("Arial", 24),
            text_color="#9ca3af"
        )
        subtitle_label.place(relx=0.5, rely=0.33, anchor="center")

        # Play button
        play_button = ctk.CTkButton(
            self.startScreen,
            text="▶ PLAY NOW",
            command=self.show_game_screen,
            font=("Arial", 26, "bold"),
            width=250,
            height=60,
            fg_color="#4a90e2",
            hover_color="#357abd",
            corner_radius=10
        )
        play_button.place(relx=0.5, rely=0.45, anchor="center")

        # How to Play button
        how_to_play_button = ctk.CTkButton(
            self.startScreen,
            text="❓ How to Play",
            command=self.show_how_to_play_screen,
            font=("Arial", 26, "bold"),
            width=250,
            height=60,
            fg_color="#4ade80",
            hover_color="#22c55e",
            corner_radius=10
        )
        how_to_play_button.place(relx=0.5, rely=0.55, anchor="center")

        # Exit button
        exit_button = ctk.CTkButton(
            self.startScreen,
            text="✕ Exit",
            command=self.destroy,
            font=("Arial", 26, "bold"),
            width=250,
            height=60,
            fg_color=COLOR_ERROR,
            hover_color="#cc3333",
            text_color=TEXT_COLOR,
            corner_radius=8
        )
        exit_button.place(relx=0.5, rely=0.65, anchor="center")

    def show_game_screen(self):
        self.clear_screen()
        self.setup_new_game()
        self.create_game_widget()

    def show_how_to_play_screen(self):
        self.clear_screen()
        self.howToPlayScreen = ctk.CTkFrame(self, fg_color=BACKGROUND_COLOR)
        self.howToPlayScreen.pack(expand=True, fill="both")

        # Create scrollable frame for content
        scrollable = ctk.CTkScrollableFrame(
            self.howToPlayScreen,
            fg_color=BACKGROUND_COLOR,
            width=900,
            height=900
        )
        scrollable.pack(expand=True, fill="both", padx=50, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            scrollable,
            text="📖 How to Play",
            font=("Arial", 42, "bold"),
            text_color="#4ade80"
        )
        title_label.pack(pady=(10, 20))

        # Game Objective
        objective_frame = ctk.CTkFrame(scrollable, fg_color="#2b2b2b", corner_radius=10)
        objective_frame.pack(fill="x", padx=20, pady=10)
        
        obj_title = ctk.CTkLabel(
            objective_frame,
            text="🎯 Game Objective",
            font=("Arial", 24, "bold"),
            text_color="#60a5fa"
        )
        obj_title.pack(pady=(15, 10), padx=20, anchor="w")
        
        obj_text = ctk.CTkLabel(
            objective_frame,
            text="Your goal is to identify the mystery country from its silhouette (outline shape).\nYou'll see the country's shape but not its name. Use your geography knowledge to guess!",
            font=("Arial", 16),
            text_color=TEXT_COLOR,
            justify="left"
        )
        obj_text.pack(pady=(0, 15), padx=30, anchor="w")

        # How to Guess
        guess_frame = ctk.CTkFrame(scrollable, fg_color="#2b2b2b", corner_radius=10)
        guess_frame.pack(fill="x", padx=20, pady=10)
        
        guess_title = ctk.CTkLabel(
            guess_frame,
            text="✍️ How to Make a Guess",
            font=("Arial", 24, "bold"),
            text_color="#60a5fa"
        )
        guess_title.pack(pady=(15, 10), padx=20, anchor="w")
        
        guess_text = ctk.CTkLabel(
            guess_frame,
            text="1. Type the country name in the input box\n2. Use the dropdown suggestions to help you find countries\n3. Press Enter or click the Enter button to submit your guess\n4. You can guess as many times as you want!",
            font=("Arial", 16),
            text_color=TEXT_COLOR,
            justify="left"
        )
        guess_text.pack(pady=(0, 15), padx=30, anchor="w")

        # Understanding Feedback
        feedback_frame = ctk.CTkFrame(scrollable, fg_color="#2b2b2b", corner_radius=10)
        feedback_frame.pack(fill="x", padx=20, pady=10)
        
        feedback_title = ctk.CTkLabel(
            feedback_frame,
            text="📊 Understanding the Feedback",
            font=("Arial", 24, "bold"),
            text_color="#60a5fa"
        )
        feedback_title.pack(pady=(15, 10), padx=20, anchor="w")
        
        feedback_text = ctk.CTkLabel(
            feedback_frame,
            text="After each guess, you'll see helpful information:",
            font=("Arial", 16),
            text_color=TEXT_COLOR,
            justify="left"
        )
        feedback_text.pack(pady=(0, 10), padx=30, anchor="w")

        # Example guesses
        example_label = ctk.CTkLabel(
            feedback_frame,
            text="Example Guesses:",
            font=("Arial", 18, "bold"),
            text_color="#4ade80"
        )
        example_label.pack(pady=(10, 10), padx=30, anchor="w")

        # Example 1: Vietnam
        example1_frame = ctk.CTkFrame(
            feedback_frame,
            fg_color="#70e7fb",
            corner_radius=8,
            height=45
        )
        example1_frame.pack(fill="x", padx=40, pady=5)
        example1_frame.grid_propagate(False)
        
        example1_frame.columnconfigure(0, weight=4)
        example1_frame.columnconfigure(1, weight=1)
        example1_frame.columnconfigure(2, weight=0)
        example1_frame.rowconfigure(0, weight=1)

        ex1_country = ctk.CTkLabel(example1_frame, text="Vietnam", font=("Arial", 14), text_color="#2b2b2b", anchor="w")
        ex1_country.grid(row=0, column=0, padx=15, pady=8, sticky="w")
        
        ex1_distance = ctk.CTkLabel(example1_frame, text="~ 1,245km", font=("Arial", 14), text_color="#2b2b2b", anchor="center")
        ex1_distance.grid(row=0, column=1, padx=10, pady=8, sticky="e")
        
        ex1_arrow_frame = ctk.CTkFrame(example1_frame, fg_color="#5c9fd6", corner_radius=6, width=40, height=35)
        ex1_arrow_frame.grid(row=0, column=2, padx=8, pady=5, sticky="e")
        ex1_arrow_frame.grid_propagate(False)
        
        ex1_arrow = ctk.CTkLabel(ex1_arrow_frame, text="↗", font=("Arial", 20, "bold"), text_color="white")
        ex1_arrow.place(relx=0.5, rely=0.5, anchor="center")

        # Example 2: Thailand
        example2_frame = ctk.CTkFrame(
            feedback_frame,
            fg_color="#70e7fb",
            corner_radius=8,
            height=45
        )
        example2_frame.pack(fill="x", padx=40, pady=5)
        example2_frame.grid_propagate(False)
        
        example2_frame.columnconfigure(0, weight=4)
        example2_frame.columnconfigure(1, weight=1)
        example2_frame.columnconfigure(2, weight=0)
        example2_frame.rowconfigure(0, weight=1)

        ex2_country = ctk.CTkLabel(example2_frame, text="Thailand", font=("Arial", 14), text_color="#2b2b2b", anchor="w")
        ex2_country.grid(row=0, column=0, padx=15, pady=8, sticky="w")
        
        ex2_distance = ctk.CTkLabel(example2_frame, text="~ 523km", font=("Arial", 14), text_color="#2b2b2b", anchor="center")
        ex2_distance.grid(row=0, column=1, padx=10, pady=8, sticky="e")
        
        ex2_arrow_frame = ctk.CTkFrame(example2_frame, fg_color="#5c9fd6", corner_radius=6, width=40, height=35)
        ex2_arrow_frame.grid(row=0, column=2, padx=8, pady=5, sticky="e")
        ex2_arrow_frame.grid_propagate(False)
        
        ex2_arrow = ctk.CTkLabel(ex2_arrow_frame, text="←", font=("Arial", 20, "bold"), text_color="white")
        ex2_arrow.place(relx=0.5, rely=0.5, anchor="center")

        # Explanation
        explanation_text = ctk.CTkLabel(
            feedback_frame,
            text="""
• Country Name: The country you guessed
• Distance: Approximate distance from your guess to the target country (in kilometers)
• Arrow Direction: Shows which direction the target country is located
  ↑ = North    ↓ = South    ← = West    → = East
  ↗ = Northeast    ↘ = Southeast    ↙ = Southwest    ↖ = Northwest

💡 Strategy: Use the distance and direction to narrow down your next guess!
If the distance gets smaller, you're getting closer to the correct answer!""",
            font=("Arial", 15),
            text_color=TEXT_COLOR,
            justify="left"
        )
        explanation_text.pack(pady=(10, 20), padx=30, anchor="w")

        # Tips
        tips_frame = ctk.CTkFrame(scrollable, fg_color="#2b2b2b", corner_radius=10)
        tips_frame.pack(fill="x", padx=20, pady=10)
        
        tips_title = ctk.CTkLabel(
            tips_frame,
            text="💡 Tips & Tricks",
            font=("Arial", 24, "bold"),
            text_color="#60a5fa"
        )
        tips_title.pack(pady=(15, 10), padx=20, anchor="w")
        
        tips_text = ctk.CTkLabel(
            tips_frame,
            text="• Study the shape carefully - look for distinctive features\n• Use the arrow directions to triangulate the target location\n• Start with countries you know well from a region\n• The distance helps you understand how far off you are\n• Don't give up! You have unlimited guesses",
            font=("Arial", 16),
            text_color=TEXT_COLOR,
            justify="left"
        )
        tips_text.pack(pady=(0, 15), padx=30, anchor="w")

        # Back button
        back_button = ctk.CTkButton(
            scrollable,
            text="← Back to Menu",
            command=self.show_start_screen,
            font=("Arial", 20, "bold"),
            width=200,
            height=50,
            fg_color="#6b7280",
            hover_color="#4b5563",
            corner_radius=10
        )
        back_button.pack(pady=30)

    def show_end_screen(self, win):
        self.clear_screen()
        self.endScreen = ctk.CTkFrame(self, fg_color=BACKGROUND_COLOR)
        self.endScreen.pack(expand=True, fill="both")

        if win:
            # Win screen
            title_label = ctk.CTkLabel(
                self.endScreen,
                text="🎉 Congratulations! 🎉",
                font=("Arial", 28, "bold"),
                text_color="#4ade80"
            )
            title_label.pack(pady=10)

            result_label = ctk.CTkLabel(
                self.endScreen,
                text=f"You guessed it in {len(self.guessedCountries)} tries!",
                font=("Arial", 18),
                text_color=TEXT_COLOR
            )
            result_label.pack(pady=5)
        else:
            # Lose screen
            title_label = ctk.CTkLabel(
                self.endScreen,
                text="😢 Game Over 😢",
                font=("Arial", 28, "bold"),
                text_color=COLOR_ERROR
            )
            title_label.pack(pady=10)

            result_label = ctk.CTkLabel(
                self.endScreen,
                text="Better luck next time!",
                font=("Arial", 18),
                text_color=TEXT_COLOR
            )
            result_label.pack(pady=5)

        # Display the secret country image (smaller size)
        # Resize image to 300x300 for end screen with white background
        svg_path = f"{COUNTRY_IMAGE_PATH}{self.secretCountry}.svg"
        png_data = cairosvg.svg2png(url=svg_path, output_width=300, output_height=300, background_color='white')
        pil_image = Image.open(io.BytesIO(png_data))
        smaller_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(300, 300))
        
        svg_label = ctk.CTkLabel(self.endScreen, image=smaller_image, text="")
        svg_label.pack(pady=10)

        # Display the answer
        answer_label = ctk.CTkLabel(
            self.endScreen,
            text=f"The answer was: {self.secretCountryData['Country Name']}",
            font=("Arial", 22, "bold"),
            text_color="#60a5fa"
        )
        answer_label.pack(pady=5)

        # Display additional country information
        info_frame = ctk.CTkFrame(self.endScreen, fg_color="#2b2b2b", corner_radius=10)
        info_frame.pack(pady=8, padx=20)

        info_text = f"Population: {self.secretCountryData['Population']:,}  |  Area: {self.secretCountryData['Area']:,} km²  |  Coordinates: {self.secretCountryData['Latitude']:.2f}°, {self.secretCountryData['Longitude']:.2f}°"
        
        info_label = ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=("Arial", 14),
            text_color=TEXT_COLOR,
            justify="center"
        )
        info_label.pack(padx=20, pady=10)

        # Buttons frame
        button_frame = ctk.CTkFrame(self.endScreen, fg_color="transparent")
        button_frame.pack(pady=15)

        # Play Again button
        play_again_button = ctk.CTkButton(
            button_frame,
            text="Play Again",
            command=self.show_game_screen,
            font=("Arial", 18),
            width=160,
            height=45,
            fg_color="#4a90e2",
            hover_color="#357abd"
        )
        play_again_button.pack(side="left", padx=10)

        # Main Menu button
        main_menu_button = ctk.CTkButton(
            button_frame,
            text="Main Menu",
            command=self.show_start_screen,
            font=("Arial", 18),
            width=160,
            height=45,
            fg_color="#6b7280",
            hover_color="#4b5563"
        )
        main_menu_button.pack(side="left", padx=10)

    # Game logic methods
    def setup_new_game(self):
        """"Thiết lập trò chơi mới"""
        self.clear_screen()
        self.secretCountry = random.choice(list(self.countryData.keys()))
        print(f"Secret country selected: {self.countryData[self.secretCountry]['Country Name']}")
        if (self.secretCountry in self.countryImages):
            print("SVG image loaded for the secret country.")
        else:
            svg_path = f"{COUNTRY_IMAGE_PATH}{self.secretCountry}.svg"
            png_data = cairosvg.svg2png(url=svg_path, output_width=400, output_height=400, background_color='white')
            pil_image = Image.open(io.BytesIO(png_data))
            self.countryImages[self.secretCountry] = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(400, 400))
        self.secretCountryData = self.countryData[self.secretCountry]
        self.secretCountryImage = self.countryImages[self.secretCountry]

        self.guessedCountries = []
        self.selectedIndex = -1
        self.curSuggestions = []

    def create_game_widget(self):
        self.gameScreen = ctk.CTkFrame(self, fg_color=BACKGROUND_COLOR)
        self.gameScreen.pack(expand=True, fill="both")

        # entry frame
        entryFrame = ctk.CTkFrame(
            self.gameScreen, 
            fg_color="transparent",
            width=620,
            height=50
        )
        entryFrame.pack(pady=20)
        entryFrame.pack_propagate(False)
        
        # Entry để nhập tên nước
        self.entry = ctk.CTkEntry(
            entryFrame, 
            font=FONT_SMALL, 
            width=400, 
            height=40, 
            border_width=2,
            placeholder_text="Enter country name...",
            fg_color="#2b2b2b",      
            border_color="#565b5e",      
            text_color=TEXT_COLOR,        
            placeholder_text_color="#7a7a7a",  
            corner_radius=6
        )
        self.entry.place(x=0, y=5)
        self.entry.bind('<KeyRelease>', self.on_key_release)

        enterButton = ctk.CTkButton(
            entryFrame,
            text="Enter",
            font=FONT_SMALL,
            width=80,
            height=40,
            command=self.pressEnter,
            fg_color="#4a90e2",
            hover_color="#357abd",
            corner_radius=6
        )
        enterButton.place(x=410, y=5)
        
        giveUpButton = ctk.CTkButton(
            entryFrame,
            text="Give Up",
            font=FONT_SMALL,
            width=100,
            height=40,
            command=lambda: self.show_end_screen(win=False),
            fg_color=COLOR_ERROR,
            hover_color="#cc3333",
            corner_radius=6
        )
        giveUpButton.place(x=500, y=5)
        
        self.bind('<Return>', lambda event: self.pressEnter())
        self.entry.bind('<Down>', lambda event: self.navigateDown())
        self.entry.bind('<Up>', lambda event: self.navigateUp())
        
        # SVG image của nước bí mật
        svg_label = ctk.CTkLabel(self.gameScreen, image=self.secretCountryImage, text="")
        svg_label.pack(pady=20)

        # Frame cha để giới hạn chiều rộng
        scrollableFrame = ctk.CTkFrame(self.gameScreen, fg_color="transparent", width=800, height=400)
        scrollableFrame.pack(pady=10)
        scrollableFrame.pack_propagate(False) 

        # List box các nước đã đoán        
        self.listBoxGuessed = ctk.CTkScrollableFrame(scrollableFrame, label_text="Countries Guessed")
        self.listBoxGuessed.pack(fill="both", expand=True)
        self.updateGuessList()
        
        # Text box gợi ý các nước
        self.textBoxFrame = ctk.CTkFrame(self.gameScreen, fg_color="transparent", width=400, height=150)
        self.textBoxFrame.place(x=458, y=70)
        self.textBoxFrame.pack_propagate(False)
        self.textBoxSuggestions = ctk.CTkTextbox(
            self.textBoxFrame,
            font=("Arial", 15),
            width=400,
            height=150,
            wrap="none",
            border_width=2,
            border_color="#0095f2"
        )
        self.textBoxSuggestions.pack(fill="both", expand=True)
        self.textBoxFrame.lift()  
        self.textBoxFrame.place_forget()
        self.curSuggestions = []

        self.textBoxSuggestions.bind('<Button-1>', self.on_select)

    def updateGuessList(self):
        for widget in self.listBoxGuessed.winfo_children():
            widget.destroy()
        
        if (not self.guessedCountries):
            label = ctk.CTkLabel(self.listBoxGuessed, text="No countries guessed yet...", text_color="gray")
            label.pack(pady=5)
        else:
            for countryCode in reversed(self.guessedCountries):
                countryName = self.countryData[countryCode]["Country Name"]
                guessFrame = ctk.CTkFrame(
                    self.listBoxGuessed,
                    fg_color="#70e7fb",
                    corner_radius=8,
                    height=45
                )
                guessFrame.pack(fill="x", padx=10, pady=3)

                # Cấu hình grid để expand
                guessFrame.columnconfigure(0, weight=3)  # Column 0 (tên nước) chiếm nhiều nhất
                guessFrame.columnconfigure(1, weight=1)  # Column 1 (khoảng cách)
                guessFrame.columnconfigure(2, weight=0)  # Column 2 (mũi tên) - width cố định
                guessFrame.rowconfigure(0, weight=1)

                # Label tên nước với cờ
                countryLabel = ctk.CTkLabel(
                    guessFrame, 
                    text=f"{countryName}",
                    font=("Arial", 14),
                    text_color="#2b2b2b",
                    anchor="w"
                )
                countryLabel.grid(row=0, column=0, padx=15, pady=8, sticky="w")

                distance, arrow = get_distance_and_arrow(self.countryData[countryCode], self.secretCountryData)

                # Label khoảng cách
                distanceLabel = ctk.CTkLabel(
                    guessFrame, 
                    text=f"~ {distance}km",
                    font=("Arial", 14),
                    text_color="#2b2b2b",
                    anchor="center"
                )
                distanceLabel.grid(row=0, column=1, padx=10, pady=8, sticky="e")

                # Label mũi tên với background xanh dương
                arrowFrame = ctk.CTkFrame(
                    guessFrame,
                    fg_color="#5c9fd6",
                    corner_radius=6,
                    width=40,
                    height=35
                )
                arrowFrame.grid(row=0, column=2, padx=8, pady=5, sticky="e")
                arrowFrame.grid_propagate(False)

                arrowLabel = ctk.CTkLabel(
                    arrowFrame,
                    text=arrow,
                    font=("Arial", 20, "bold"),
                    text_color="white"
                )
                arrowLabel.place(relx=0.5, rely=0.5, anchor="center")

    def on_key_release(self, event):
        """Xử lý khi người dùng nhập từ"""
        if (event and event.keysym in ['Up', 'Down']):
            return
        prefix = self.entry.get().strip().lower()
        
        # Xóa danh sách gợi ý cũ
        self.textBoxSuggestions.configure(state="normal")
        self.textBoxSuggestions.delete("1.0", "end")
        
        if prefix:
            # Tìm các từ có prefix khớp
            suggestions = []
            for countryCode, data in self.countryData.items():
                countryName = data["Country Name"]
                if countryName.lower().startswith(prefix):
                    suggestions.append(countryName)
            
            # Hiển thị gợi ý trong textbox
            if suggestions:
                self.curSuggestions = suggestions
                for suggestion in suggestions:
                    self.textBoxSuggestions.insert("end", suggestion + "\n")
                self.textBoxFrame.place(x=458, y=70)
                self.textBoxFrame.lift()
            else:
                self.curSuggestions = []
                self.textBoxSuggestions.insert("end", "No suggestions found.")
                self.textBoxFrame.place(x=458, y=70)
                self.textBoxFrame.lift()
        else:
            self.textBoxFrame.place_forget() 
        
        self.textBoxSuggestions.configure(state="disabled")

    def highlight_selection(self):
        """Highlight dòng được chọn"""
        self.textBoxSuggestions.configure(state="normal")
        self.textBoxSuggestions.tag_remove("highlight", "1.0", "end")
        if 0 <= self.selectedIndex < len(self.curSuggestions):
            start_index = f"{self.selectedIndex + 1}.0"
            end_index = f"{self.selectedIndex + 1}.end"
            self.textBoxSuggestions.tag_add("highlight", start_index, end_index)
            self.textBoxSuggestions.tag_config("highlight", background="#0095f2", foreground="white")
            self.textBoxSuggestions.see(start_index)
        self.textBoxSuggestions.configure(state="disabled")

    def selectLine(self, line_number):
        """Xử lý khi click vào một từ trong danh sách gợi ý"""
        try:
            if 0 <= line_number < len(self.curSuggestions):
                self.selectedIndex = line_number
                # Lấy từ được chọn
                selected_word = self.curSuggestions[line_number]
                # Cập nhật entry với từ được chọn
                self.entry.delete(0, 'end')
                self.entry.insert(0, selected_word)
                # self.on_key_release(None)
                self.highlight_selection()
                # self.textBoxFrame.place_forget()

        except (IndexError, ValueError):
            pass 

    def on_select(self, event):
        """Xử lý khi click vào một từ trong danh sách gợi ý"""
        try:
            # Lấy vị trí click
            index = self.textBoxSuggestions.index(f"@{event.x},{event.y}")
            line_number = int(index.split('.')[0]) - 1  # Lấy số dòng (bắt đầu từ 0)
            
            self.selectLine(line_number)

        except (IndexError, ValueError):
            pass 

    def navigateUp(self):
        """Xử lý khi bấm phím mũi tên lên"""
        if len(self.curSuggestions) == 0:
            return 'break'
        
        self.selectedIndex -= 1
        if self.selectedIndex < 0:
            self.selectedIndex = len(self.curSuggestions) - 1

        self.selectLine(self.selectedIndex)
        
    def navigateDown(self):
        """Xử lý khi bấm phím mũi tên xuống"""
        if len(self.curSuggestions) == 0:
            return 'break'
        
        self.selectedIndex += 1
        if self.selectedIndex >= len(self.curSuggestions):
            self.selectedIndex = 0

        self.selectLine(self.selectedIndex)

    def pressEnter(self): # Press Enter
        """Xử lý khi nhấn nút Enter"""
        print(self.entry.get())
        if (self.entry.get().strip().lower() in self.countryNametoCode):
            countryCode = self.countryNametoCode[self.entry.get().strip().lower()]
            
            if countryCode not in self.guessedCountries: # Nếu chưa đoán nước này
                self.guessedCountries.append(countryCode)
                self.updateGuessList()
            else:
                self.trigger_error_toast("You already guessed this country!")

            self.entry.delete(0, 'end')
            self.textBoxFrame.place_forget()
            self.selectedIndex = -1
            self.curSuggestions = []

            if (countryCode == self.secretCountry):
                self.show_end_screen(win=True)
                return
        
        else:
            self.trigger_error_toast("Invalid country name!")


if __name__ == "__main__":
    app = GameApp()
    app.mainloop()

    