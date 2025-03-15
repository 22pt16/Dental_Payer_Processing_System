
### `README.md`

```markdown
# Dental Insurance Payer Processing System

![Alt Text](output.png)
## Problem Statement
In the dental insurance industry, payments from insurance companies (payers) are processed via Electronic Remittance Advice (ERA) documents. This project designs and implements a system to manage payer information complexity across multiple data sources, addressing inconsistencies, deduplication, and display name standardization.

### Current Challenges
1. **Inconsistent Payer Information**:
   - ERA payments link payers inconsistently (e.g., initial payer with number vs. DentalXChange ERA without number).
2. **Payer Deduplication**:
   - System tracks payer groups (e.g., Delta Dental) but struggles to deduplicate similar payers (e.g., "DELTA DENTAL OF ARIZONA, 86027" vs. "DELTA DENTAL OF ARIZONA, CDKY1").
3. **Display Name Issues**:
   - No standardized "pretty names" for consistent UI/claims representation.

### Payer Structure
- **Payer_Details**: Raw payer instances from payment documents.
  - Examples:
    - "DELTA DENTAL OF ARIZONA | 86027 | (no EIN)"
    - "DELTA DENTAL OF ARIZONA | (no payer number) | 1860274899"
    - "FENWICK & WEST LLP | 62308 | (no EIN)" (same as "TOWER RESEARCH CAPITAL LLC | 62308")
- **Payers**: Unique insurance companies within payer groups.
  - Examples:
    - "Delta Dental of Arizona" (Delta Dental group)
    - "Delta Dental of California" (Delta Dental group)
- **Payer_Groups**: Parent organizations owning multiple payers.
  - Example: "Delta Dental"

### Edge Cases
1. Different names, same payer number → different payers.
2. Different names, same payer number → same payer.
3. Same name, different payer numbers → same payer.
4. Slightly varying names → semantically same payer.

## Solution

### 1. Database Schema Design
- **Tables**:
  - `payer_groups`:
    - `group_id` (PK), `group_name`
  - `payers`:
    - `payer_id` (PK), `payer_name`, `pretty_name`, `group_id` (FK to `payer_groups`)
  - `payer_details`:
    - `detail_id` (PK), `payer_name`, `payer_id` (FK to `payers`), `source`, `state`
- **Relationships**:
  - One `payer_group` to many `payers` (1:N).
  - One `payer` to many `payer_details` (1:N).
- **Normalization**: Handles examples and edge cases (e.g., same `payer_id` with different names).

### 2. Mapping Algorithm
- **Logic** (`routes.py`):
  - **Fuzzy Matching**: Uses `fuzzywuzzy` (70-85% similarity) to identify unmapped `payer_details`.
  - **Deduplication**: 
    - Groups `payer_details` by `payer_id` or semantic similarity to canonical `payers`.
    - Handles edge cases via manual mapping UI.
  - **Output**: Maps raw payers from Excel into `payers` and `payer_details` tables.
- **Endpoints**:
  - `/api/unmapped`: Identifies and paginates unmapped details.
  - `/api/map_payer`: Links `payer_details` to `payers`.

### 3. User Interface
- **Components** (`App.jsx`):
  - **Unmapped Payers**:
    - Paginated table with dropdown for manual mapping.
  - **Pretty Names**:
    - Paginated table with editable inputs; auto-generates PascalCase names (e.g., "DeltaDental").
  - **Payer Hierarchies**:
    - Grouped view by `group_id`, with dropdown for reassignment and new group creation.
- **Features**:
  - PascalCase formatting for all names.
  - Sorted group dropdown.


## Setup
### Prerequisites
- Python 3.8+
- SQLite

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
- Open `http://localhost:5173`.

## Usage
- **Mapping**: Map unmapped payers via dropdown in "Unmapped Payers".
- **Pretty Names**: Edit and save in "Pretty Names".
- **Hierarchies**: Assign/manage groups in "Payer Hierarchies".

## Edge Case Handling
- **Different Names, Same Payer Number**: Manual mapping resolves ambiguity.
- **Same Name, Different Numbers**: Fuzzy matching + manual override.
- **Semantic Matching**: 70-85% similarity threshold with UI confirmation.
- - Nested groups (e.g., "DeltaDental" > "DeltaDentalArizona").

## Future Enhancements
- Collapsible hierarchy sections.
- API for all groups without pagination.

## Data Source
- Refer to the attached Excel sheet for raw payer data to map into canonical payers.



