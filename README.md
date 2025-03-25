```markdown
# Dental Insurance Payer Processing System

![System Workflow](output.png)

## Overview
The **Dental Insurance Payer Processing System** efficiently processes Electronic Remittance Advice (ERA) documents by resolving inconsistencies, deduplicating payer information, and standardizing display names for accurate claims processing.

## Key Challenges
1. **Inconsistent Payer Information:**  
   - ERA payments reference payers inconsistently (e.g., initial payer with number vs. DentalXChange ERA without number).
2. **Payer Deduplication:**  
   - Deduplication of payers with slight variations in names or payer numbers (e.g., `"DELTA DENTAL OF ARIZONA, 86027"` vs. `"DELTA DENTAL OF ARIZONA, CDKY1"`).
3. **Display Name Standardization:**  
   - Lack of canonical names ("pretty names") for consistent UI and claims representation.

---

## Tech Stack
- **Backend:** Flask (Python 3.8+)  
- **Frontend:** React (Vite)  
- **Database:** PostgreSQL  
- **Fuzzy Matching:** `fuzzywuzzy` for identifying and mapping similar payers.  

---

## System Architecture

### Database Schema Design
- **Tables:**
   - `payer_groups`: Stores parent organizations (`group_id`, `group_name`).
   - `payers`: Stores unique payer entities (`payer_id`, `payer_name`, `pretty_name`, `group_id`).
   - `payer_details`: Holds raw payer details (`detail_id`, `payer_name`, `payer_id`, `source`, `state`).

- **Relationships:**
   - One `payer_group` → Many `payers` (1:N).
   - One `payer` → Many `payer_details` (1:N).
- **Normalization:** Ensures deduplication and consistent mapping of raw payers.

---

### Mapping and Deduplication Algorithm
- **Fuzzy Matching:**
   - Utilizes `fuzzywuzzy` with a 70-85% similarity threshold to identify and map unmapped `payer_details`.
- **Deduplication Logic:**
   - Groups `payer_details` by `payer_id` or semantic similarity to canonical `payers`.
   - Manual mapping available via the UI for edge cases.
- **API Endpoints:**
   - `/api/unmapped`: Retrieves and paginates unmapped payer details.
   - `/api/map_payer`: Maps `payer_details` to canonical `payers`.

---

### User Interface
- **Components:**
   - **Unmapped Payers:** Paginated table with manual mapping dropdown.
   - **Pretty Names:** Editable inputs for standardizing payer names to PascalCase.
   - **Payer Hierarchies:** Grouped view of `payer_groups` with options to assign/reassign payers and create new groups.

- **Features:**
   - Consistent PascalCase formatting.
   - Grouped dropdowns for efficient navigation.
   - Manual override for ambiguous mappings.

---

## Setup Instructions

### Prerequisites
- Python 3.8+
- PostgreSQL
- Node.js 14+

---

### Backend Setup

# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Mac/Linux
# OR
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_APP=app.py
export DATABASE_URL=postgresql://username:password@localhost/payer_db

# Run Flask application
flask run


---

### Frontend Setup

# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev

- Access the UI at `http://localhost:5173`.

---

## Usage Guide
- **Map Unmapped Payers:** Assign raw payer details to canonical payers.
- **Standardize Pretty Names:** Edit and save canonical payer names.
- **Manage Hierarchies:** Group payers into logical hierarchies for better management.

---

## Edge Case Handling
1. **Different Names, Same Payer Number:** Manual mapping resolves ambiguity.
2. **Same Name, Different Numbers:** Fuzzy matching + manual override.
3. **Semantic Matching:** 70-85% similarity threshold with UI confirmation.
4. **Nested Groups:** Supports hierarchical groupings (e.g., `DeltaDental` → `DeltaDentalArizona`).

---

## API Documentation
- `/api/unmapped` – Retrieves unmapped payers.
- `/api/map_payer` – Maps payer details to canonical payers.
- `/api/groups` – Retrieves all payer groups with hierarchies.

---

## Future Enhancements
- Collapsible hierarchy views for grouped payers.
- API to retrieve all groups without pagination.
- Integration of machine learning models for improved fuzzy matching.

---

## Data Source
The system processes ERA documents from multiple sources, ensuring consistency and deduplication across payer information.
