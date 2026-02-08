# Mapper

An AI-powered tour planning and guide matching system for Oxford (and other cities). Built with Streamlit, featuring a mobile-first UI with a 5-step booking flow.

## What it does

1. **Setup** — Pick your date, city, languages, attractions, guide type, and budget
2. **Routes** — AI generates 5 themed route plans (Fastest, Popular, Balanced, Relaxed, Hidden Gems)
3. **Match** — Finds compatible guides with dynamic pricing based on date, route, and demand
4. **Confirm** — Review your trip details, route, guide, and total price
5. **Sent** — Booking request sent with a reference ID

## Screenshots

The app features a mobile-first design (480px max-width) with:
- Hero banner with gradient background
- Clickable image cards for guide type selection
- Color-coded route timelines
- Driver cards with photos and live pricing
- Step indicator showing booking progress

## Project Structure

```
EHT_Oxford/
├── ui.py                      # Streamlit UI (5-page flow)
├── trip_request.py            # Trip request data model
├── travel_planner/
│   ├── response.py            # AI route generation
│   ├── models.py              # Attraction, Route, Timeline models
│   └── attraction_filter.py   # CSV-based attraction loading
├── driver.py                  # Driver loading & scoring
├── active_pricing/
│   └── pricing.py             # Dynamic pricing engine
├── loading_files.py           # CSV helpers (languages, attractions)
├── data_collection/
│   └── Database/
│       └── driver_identifier.csv  # Driver database (600 drivers)
├── photos/                    # Driver avatar photos (PNG, circular)
│   ├── driver_0.png
│   ├── driver_1.png
│   ├── driver_2.png
│   ├── driver_3.png
│   └── driver_4.png
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

### Prerequisites
- Python 3.10+
- OpenAI API key (for route generation)

### Installation

```bash
git clone <repo-url>
cd EHT_Oxford
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file or export:

```bash
export OPENAI_API_KEY=your_key_here
```

### Run

```bash
streamlit run ui.py
```

Open the **Network URL** on your phone for the mobile experience.

## Key Features

### AI Route Generation
Generates 5 themed routes using AI, each with:
- Optimised attraction ordering
- Travel time estimates between stops
- Random visit durations (30–60 min per attraction)
- Micro-stop suggestions nearby

### Dynamic Pricing
Prices adjust based on:
- Date (weekends, holidays cost more)
- Route complexity (number of stops, total duration)
- Driver compatibility score
- Budget constraints

### Guide Matching
Scores 600 drivers on:
- Language compatibility
- Attraction knowledge
- Service type match (Buddy, Bike Guide, Driver Guide, Driver Only)
- Availability on chosen date
- Overall rating

## Tech Stack

- **Frontend**: Streamlit with custom CSS (mobile-first, 480px)
- **AI**: OpenAI API for route planning
- **Data**: CSV-based driver and attraction databases
- **Pricing**: Custom dynamic pricing engine with holiday/demand adjustments
- **Fonts**: Playfair Display (headings), DM Sans (body)

## License

Proprietary — all rights reserved.