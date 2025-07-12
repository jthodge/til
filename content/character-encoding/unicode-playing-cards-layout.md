# Unicode playing cards layout

You can represent playing cards in unicode.
The representative pattern for each card's structure directly maps to card values and suits.

## Code point structure

Unicode playing cards follow a predictable pattern:
- Last digit: card's point value (aces low)
- Second-to-last digit: suit

Base pattern starting at `U+1F0A1` (ace of spades):
- Spades: `U+1F0A*`
- Hearts: `U+1F0B*`
- Diamonds: `U+1F0C*`
- Clubs: `U+1F0D*`

## Card value mapping

```python
# Display all Unicode playing cards
for i in range(4):
    for j in range(14):
        print(chr(0x1f0a1 + j + 16*i), end='')
    print()
```

Individual cards, e.g.:
```python
# Specific cards
print(chr(0x1F0A1))  # 🂡 Ace of spades
print(chr(0x1F0B1))  # 🂱 Ace of hearts
print(chr(0x1F0C1))  # 🃁 Ace of diamonds
print(chr(0x1F0D1))  # 🃑 Ace of clubs

print(chr(0x1F0A3))  # 🂣 Three of spades
print(chr(0x1F0B7))  # 🂷 Seven of hearts
print(chr(0x1F0CE))  # 🃎 King of diamonds
```

## The hidden knight cards

Unicode includes knight cards that don't exist in standard 52-card decks:
- Jacks end in B (hex B = 11)
- Knights end in C (hex C = 12)
- Queens end in D (hex D = 13)
- Kings end in E (hex E = 14)

```python
# Face cards demonstration
suits = ['spades', 'hearts', 'diamonds', 'clubs']
for i, suit in enumerate(suits):
    base = 0x1F0A1 + (16 * i)
    print(f"{suit}:")
    print(f"  Jack:   {chr(base + 0x0B)}")
    print(f"  Knight: {chr(base + 0x0C)}")  # Not in standard deck!
    print(f"  Queen:  {chr(base + 0x0D)}")
    print(f"  King:   {chr(base + 0x0E)}")
```

## Full deck generator

```python
def generate_standard_deck():
    """Generate a standard 52-card deck using Unicode."""
    deck = []
    suits = ['♠', '♥', '♦', '♣']

    for i in range(4):
        base = 0x1F0A1 + (16 * i)
        # Skip knight (position 12)
        for j in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14]:
            deck.append(chr(base + j - 1))

    return deck

# Shuffle and deal
import random
deck = generate_standard_deck()
random.shuffle(deck)
hand = deck[:5]
print("Your hand:", ' '.join(hand))
```

## Card game display utils

```python
def card_name(unicode_card):
    """Get readable name from Unicode card character."""
    code = ord(unicode_card)
    base = 0x1F0A1

    # Determine suit
    suit_offset = (code - base) // 16
    suits = ['spades', 'hearts', 'diamonds', 'clubs']
    suit = suits[suit_offset]

    # Determine rank
    rank_code = (code - base) % 16 + 1
    ranks = {
        1: 'ace', 2: '2', 3: '3', 4: '4', 5: '5',
        6: '6', 7: '7', 8: '8', 9: '9', 10: '10',
        11: 'jack', 12: 'knight', 13: 'queen', 14: 'king'
    }
    rank = ranks[rank_code]

    return f"{rank} of {suit}"

# E.g.
print(card_name('🂡'))  # "ace of spades"
print(card_name('🃎'))  # "king of diamonds"
```

## Terminal display considerations

Unicode playing cards require proper font support.
For terminal display:

```python
# Check if cards display properly
test_cards = ['🂡', '🂱', '🃁', '🃑']
print("Card display test:", ' '.join(test_cards))

# Alternative ASCII representation if Unicode fails
def ascii_card(rank, suit):
    """Fallback ASCII representation."""
    suit_symbols = {'spades': '♠', 'hearts': '♥',
                   'diamonds': '♦', 'clubs': '♣'}
    rank_symbols = {1: 'A', 11: 'J', 12: 'Q', 13: 'K', 14: 'K'}

    r = rank_symbols.get(rank, str(rank))
    s = suit_symbols[suit]
    return f"[{r}{s}]"
```

