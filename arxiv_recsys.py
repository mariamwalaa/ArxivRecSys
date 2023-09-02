import tkinter as tk
from tkinter import ttk
import requests
import feedparser
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm  # Progress bar

class ArXivPaperRecommendationSystem:
    def __init__(self):
        # Define the base URL for the arXiv API
        self.base_url = 'http://export.arxiv.org/api/query?'

        # Define your search query for the specified categories
        self.search_query = 'cat:math.CO+OR+cat:math.PR+OR+cat:math.ST'

        # Set the number of results you want per request
        self.results_per_query = 10

        # Initialize an empty list to store paper dictionaries
        self.papers = []

        # Initialize the progress bar
        self.pbar = None

        # Create a Tkinter window
        self.window = tk.Tk()
        self.window.title("ArXiv Paper Recommendation System")

    def retrieve_arxiv_data(self):
        """
        Retrieve academic paper data from arXiv and store it in self.papers.
        """
        # Define the total number of iterations needed
        total_iterations = 10  # For example, retrieve 10 pages of results

        # Create a progress bar
        self.pbar = tqdm(total=total_iterations, desc="Retrieving Data")

        # Perform API requests and populate the 'self.papers' list
        while total_iterations > 0:
            # Make the API request
            response = requests.get(self.base_url, params={
                'search_query': self.search_query,
                'start': len(self.papers),
                'max_results': self.results_per_query
            })

            # Parse the response using feedparser
            feed = feedparser.parse(response.text)

            # Extract paper data and add it to the list
            for entry in feed.entries:
                paper = {
                    'Title': entry.title,
                    'Summary': entry.summary
                }
                self.papers.append(paper)

            # Update progress
            self.pbar.update(1)
            total_iterations -= 1

        # Close the progress bar
        self.pbar.close()

    def calculate_similarity(self):
        """
        Calculate TF-IDF vectors and cosine similarities between papers.
        """
        # Create a DataFrame from the list of paper info
        df = pd.DataFrame(self.papers)

        # Create a TF-IDF vectorizer
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(df['Summary'])

        # Calculate cosine similarities between all pairs of papers
        similarities = cosine_similarity(tfidf_matrix, tfidf_matrix)

        # Add a new column to the DataFrame to store the similarity matrix
        df['Similarity'] = [sim for sim in similarities]

        # Create a DataFrame with just the titles and similarities for the GUI
        self.gui_df = df[['Title', 'Similarity']]

    def create_gui(self):
        """
        Create the Tkinter GUI for paper recommendations.
        """
        # Dropdown for selecting a paper title
        title_var = tk.StringVar()
        title_label = ttk.Label(self.window, text="Select a Paper Title:")
        title_label.pack()
        title_dropdown = ttk.Combobox(self.window, textvariable=title_var, values=self.gui_df['Title'].tolist())
        title_dropdown.pack()

        # Button to find similar papers
        find_button = ttk.Button(self.window, text="Find Similar Papers", command=self.find_similar_papers)
        find_button.pack()

        # Label to display similar papers
        self.result_label = ttk.Label(self.window, text="")
        self.result_label.pack()

    def find_similar_papers(self):
        """
        Find and display similar papers based on user selection.
        """
        # Get the selected paper title from the dropdown
        selected_title = title_var.get()

        # Find the index of the selected paper in the DataFrame
        selected_index = self.gui_df[self.gui_df['Title'] == selected_title].index[0]

        # Get similarity scores for the selected paper
        similarity_scores = self.gui_df['Similarity'][selected_index]

        # Sort papers by similarity and get the top 5 similar papers (excluding itself)
        similar_indices = similarity_scores.argsort()[-6:-1][::-1]
        similar_papers = self.gui_df.loc[similar_indices]

        # Display similar papers in the result label
        self.result_label.config(text="Top 5 Similar Papers:\n" + "\n".join(similar_papers['Title']))

    def run(self):
        """
        Run the ArXiv Paper Recommendation System.
        """
        # Retrieve arXiv data
        self.retrieve_arxiv_data()

        # Calculate TF-IDF vectors and similarities
        self.calculate_similarity()

        # Create the GUI
        self.create_gui()

        # Start the Tkinter main loop
        self.window.mainloop()

if __name__ == "__main__":
    # Initialize and run the ArXiv Paper Recommendation System
    recommendation_system = ArXivPaperRecommendationSystem()
    recommendation_system.run()
