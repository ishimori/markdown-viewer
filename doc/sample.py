"""
Sample Python file for Markdown Viewer testing
"""

import os
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Book:
    """Represents a book in the library"""
    title: str
    author: str
    year: int
    price: float
    category: Optional[str] = None


class Library:
    """A simple library class"""

    def __init__(self, name: str):
        self.name = name
        self.books: List[Book] = []

    def add_book(self, book: Book) -> None:
        """Add a book to the library"""
        self.books.append(book)
        print(f"Added: {book.title}")

    def find_by_author(self, author: str) -> List[Book]:
        """Find all books by a specific author"""
        return [b for b in self.books if b.author == author]

    def total_value(self) -> float:
        """Calculate total value of all books"""
        return sum(book.price for book in self.books)


def main():
    # Create a library
    library = Library("City Library")

    # Add some books
    books = [
        Book("Clean Code", "Robert Martin", 2008, 35.00, "programming"),
        Book("The Pragmatic Programmer", "David Thomas", 2019, 45.00, "programming"),
        Book("1984", "George Orwell", 1949, 12.99, "fiction"),
    ]

    for book in books:
        library.add_book(book)

    # Show total value
    print(f"\nTotal library value: ${library.total_value():.2f}")


if __name__ == "__main__":
    main()
