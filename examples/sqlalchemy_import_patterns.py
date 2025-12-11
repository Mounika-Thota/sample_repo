"""
Example: SQLAlchemy Model with String-Based Relationships
==========================================================

This file demonstrates how to handle imports for SQLAlchemy models
that are only referenced as strings in relationships.
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.db.base import Base

# Import is needed for SQLAlchemy relationship resolution
from src.models.order import Order  # noqa: F401
from src.models.payment import Payment  # noqa: F401

# ============================================================================
# Method 1: Use noqa comment (Most Explicit)
# ============================================================================


class User(Base):
    """User model with string-based relationships."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)

    # These use string references but need the imports above
    orders = relationship("Order", back_populates="user")
    payments = relationship("Payment", back_populates="user")


# ============================================================================
# Method 2: Rely on per-file-ignores (No comment needed)
# ============================================================================

# Since we configured pyproject.toml with:
# "**/models/**/*.py" = ["F401"]
#
# You can also just import without noqa:
from src.models.address import Address


class UserWithAddress(Base):
    """User model with address relationship."""

    __tablename__ = "users_with_address"

    id = Column(Integer, primary_key=True)
    username = Column(String(50))

    # String reference - import above won't trigger warnings
    address = relationship("Address", back_populates="user", uselist=False)


# ============================================================================
# Method 3: TYPE_CHECKING block for type hints
# ============================================================================

from __future__ import annotations

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    # These imports only exist during type checking, not at runtime
    from src.models.review import Review
    from src.models.wishlist import Wishlist


class UserWithTypeHints(Base):
    """User model with proper type hints."""

    __tablename__ = "users_typed"

    id = Column(Integer, primary_key=True)
    username = Column(String(50))

    # Type hints use quotes, relationships use strings
    reviews: List["Review"] = relationship("Review", back_populates="user")
    wishlist: "Wishlist" = relationship("Wishlist", back_populates="user", uselist=False)


# ============================================================================
# Method 4: Direct usage (No special handling needed)
# ============================================================================

from src.models.product import Product


class ProductCategory(Base):
    """Example where import IS directly used."""

    __tablename__ = "product_categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))

    # Direct usage in query or logic
    def get_products(self, session):
        """This directly uses the Product import - no warning."""
        return session.query(Product).filter(Product.category_id == self.id).all()


# ============================================================================
# What NOT to do (Anti-patterns)
# ============================================================================


# ❌ DON'T: Use fully qualified names
class BadExample1(Base):
    __tablename__ = "bad_example_1"

    id = Column(Integer, primary_key=True)

    # Avoid this - verbose and error-prone
    orders = relationship("src.models.order.Order", back_populates="user")


# ❌ DON'T: Import and never use
from src.models.some_random_model import SomeModel  # This IS genuinely unused!


# ❌ DON'T: Scatter imports throughout file
class BadExample2(Base):
    __tablename__ = "bad_example_2"

    id = Column(Integer, primary_key=True)

    from src.models.inline_import import InlineModel  # Don't do this!

    items = relationship("InlineModel", back_populates="owner")


# ============================================================================
# Summary
# ============================================================================
"""
Best practices for this project:

1. For model files (src/models/*.py):
   - Option A: No action needed (per-file-ignores configured)
   - Option B: Add # noqa: F401 with explanation

2. For __init__.py files:
   - Use __all__ to mark exports
   - Already configured to ignore F401

3. For type hints only:
   - Use TYPE_CHECKING block
   - Prevents circular imports
   - Clean separation

4. For direct usage:
   - Just import normally
   - No warnings will appear

Configuration in pyproject.toml:
    [tool.ruff.lint.per-file-ignores]
    "**/models/**/*.py" = ["F401"]
    "**/schemas/**/*.py" = ["F401"]
"""
