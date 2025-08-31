# AMU Pay - Hawala Money Transfer System

A comprehensive Django-based hawala money transfer system with real-time currency rates, multi-currency support, user management, secure transaction processing, and RESTful API endpoints.

## 📚 API Documentation

### Base URLs
- **API Base**: `http://localhost:8000/api/`

---

## 👨‍💼 Saraf APIs

### 1. Create Saraf Account
`POST /api/saraf-profile/create/`

**Required Fields:**
- `name` - First name
- `last_name` - Last name  
- `phone` - Phone number
- `email` - Email address
- `password` - Password
- `confirm_password` - Password confirmation
- `license_no` - License number
- `exchange_name` - Exchange business name
- `saraf_address` - Business address

**Optional Fields:**
- `province_names` - Array of province names
- `supported_currencies_input` - Array of currency objects with currency_code
- `about_us` - Description text
- `work_history` - Years of experience

**Body:**
```json
{
  "name": "Ali",
  "last_name": "Ahmadi",
  "phone": "0700123456",
  "email": "ali@example.com",
  "password": "Pass123!",
  "confirm_password": "Pass123!",
  "license_no": "LIC123456",
  "exchange_name": "Ahmadi Exchange",
  "saraf_address": "Kabul, Afghanistan",
  "province_names": ["Kabul", "Parwan"],
  "supported_currencies_input": [
    { "currency_code": "AFN" },
    { "currency_code": "USD" }
  ],
  "about_us": "We provide money exchange and remittance services.",
  "work_history": 10
}
```

**Response (201 Created):**
```json
{
  "saraf_id": 1,
  "name": "Ali",
  "last_name": "Ahmadi",
  "phone": "0700123456",
  "email": "ali@example.com",
  "license_no": "LIC123456",
  "exchange_name": "Ahmadi Exchange",
  "saraf_address": "Kabul, Afghanistan",
  "about_us": "We provide money exchange and remittance services.",
  "work_history": 10,
  "is_active": true,
  "created_at": "2024-01-15T10:00:00Z",
  "provinces": [
    {"name": "Kabul"},
    {"name": "Parwan"}
  ],
  "supported_currencies": [
    {
      "id": 1,
      "currency": {
        "id": 1,
        "code": "AFN",
        "name": "Afghan Afghani",
        "symbol": "؋"
      },
      "created_at": "2024-01-15T10:00:00Z"
    },
    {
      "id": 2,
      "currency": {
        "id": 2,
        "code": "USD",
        "name": "US Dollar",
        "symbol": "$"
      },
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

### 2. Saraf Login
`POST /api/saraf-profile/login/`

**Required Fields:**
- `password` - Password
- At least one of: `email` OR `phone`

**Optional Fields:**
- Both `email` and `phone` can be provided for extra security

**Body Options:**

**Option 1 - Login with Email:**
```json
{
  "email": "ali@example.com",
  "password": "Pass123!"
}
```

**Option 2 - Login with Phone:**
```json
{
  "phone": "0700123456",
  "password": "Pass123!"
}
```

**Option 3 - Login with Both (extra security):**
```json
{
  "email": "ali@example.com",
  "phone": "0700123456",
  "password": "Pass123!"
}
```

**Response (200 OK):**
```json
{
  "message": "Login successful",
  "saraf_id": 1,
  "name": "Ali",
  "session_id": "abcdef123456"
}
```

### 3. Saraf Logout
`POST /api/logout/`

**Response (200 OK):**
```json
{
  "message": "Logout successful"
}
```

### 4. Change Saraf Password
`POST /api/saraf-profile/{saraf_id}/change-password/`

**Required Fields:**
- `old_password` - Current password
- `new_password` - New password
- `new_password_confirm` - New password confirmation

**Body:**
```json
{
  "old_password": "Pass123!",
  "new_password": "NewPass456!",
  "new_password_confirm": "NewPass456!"
}
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

### 5. Update Saraf Logo
`PUT /api/saraf-profile/{saraf_id}/update-saraf-logo/`

**Required Fields:**
- `saraf_logo` - Image file (multipart/form-data)

**Body (multipart/form-data):**
```
saraf_logo: (file upload)
```

**Response (200 OK):**
```json
{
  "message": "saraf_logo updated",
  "saraf_id": 1
}
```

### 7. Update Saraf Logo Wallpaper
`PUT /api/saraf-profile/{saraf_id}/update-saraf-logo-wallpeper/`

**Required Fields:**
- `saraf_logo_wallpeper` - Image file (multipart/form-data)

**Body (multipart/form-data):**
```
saraf_logo_wallpeper: (file upload)
```

**Response (200 OK):**
```json
{
  "message": "saraf_logo_wallpeper updated",
  "saraf_id": 1
}
```

### 8. Update License Photo
`PUT /api/saraf-profile/{saraf_id}/update-licence-photo/`

**Required Fields:**
- `licence_photo` - Image file (multipart/form-data)

**Body (multipart/form-data):**
```
licence_photo: (file upload)
```

**Response (200 OK):**
```json
{
  "message": "licence_photo updated",
  "saraf_id": 1
}
```

### 9. Update Multiple Photos
`PUT /api/saraf-profile/{saraf_id}/update-photos/`

**Optional Fields (at least one required):**
- `saraf_logo` - Logo image file
- `saraf_logo_wallpeper` - Wallpaper image file
- `licence_photo` - License image file

**Body (multipart/form-data):**
```
saraf_logo: (file upload)
saraf_logo_wallpeper: (file upload)
licence_photo: (file upload)
```

**Response (200 OK):**
```json
{
  "message": "Photos updated successfully",
  "updated_fields": ["saraf_logo", "saraf_logo_wallpeper", "licence_photo"],
  "data": {
    "saraf_id": 1,
    "name": "Ali Ahmad",
    "exchange_name": "Ahmadi Exchange",
    "saraf_logo": "/media/saraf_photos/logo.jpg",
    "saraf_logo_wallpeper": "/media/saraf_photos/wallpaper.jpg",
    "licence_photo": "/media/saraf_photos/license.jpg"
  }
}
```

### 10. Saraf Posts

- **Create Post**: `POST /api/saraf-posts/create/`

**Auth:** Session-based. Login as Saraf first (`/api/saraf-profile/login/`).

**Content-Type:** `multipart/form-data`

**Fields:**
- `title` (required) - Post title
- `content` (optional) - Text content (required if no image)
- `image` (optional) - Image file
- `status` (optional) - One of `draft`, `published` (default: `draft`)
- `is_featured` (optional) - Boolean (default: false)

**Body (multipart/form-data):**
```
title: "New services available"
content: "We now support EUR to AFN at better rates."
image: (file upload)
status: "published"
is_featured: true
```

**Response (201 Created):**
```json
{
  "id": 1,
  "saraf": 1,
  "title": "New services available",
  "content": "We now support EUR to AFN at better rates.",
  "image": "/media/saraf_posts/post.jpg",
  "status": "published",
  "is_featured": true,
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

**Error Responses:**

- 400 Bad Request (validation):
```json
{
  "content": ["Provide content or an image"]
}
```

- 401 Unauthorized (not logged in as saraf):
```json
{
  "error": "Authentication required (saraf). Please login first."
}
```

### 10. Get Saraf Supported Currencies
`GET /api/saraf-profile/{saraf_id}/supported-currencies/?is_active={true|false}`

**Query Parameters:**
- `is_active` (optional) - Filter by active status ("true", "false", "1", "0")

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "saraf": 1,
    "currency": {
      "id": 1,
      "code": "AFN",
      "name": "Afghan Afghani",
      "symbol": "؋"
    },
    "buying_rate": "85.50",
    "selling_rate": "86.00",
    "middle_rate": "85.75",
    "is_active": true,
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

### 11. Province
- **List Provinces**: `GET /api/provinces/`

**Response (200 OK):**
```json
[
  {
    "name": "Kabul"
  },
  {
    "name": "Herat"
  }
]
```

- **Get Province by Name**: `GET /api/provinces/{name}/`

**Response (200 OK):**
```json
{
  "name": "Kabul"
}
```

### 7. Currency
- **List Currencies**: `GET /api/currencies/`

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "code": "AFN",
    "name": "Afghan Afghani",
    "symbol": "؋"
  },
  {
    "id": 2,
    "code": "USD",
    "name": "US Dollar",
    "symbol": "$"
  }
]
```

- **List Currencies with Filters**: `GET /api/currencies/?code={currency_code}&symbol={symbol}`

**Query Parameters:**
- `code` (optional) - Filter by currency code (e.g., "USD", "AFN")
- `symbol` (optional) - Filter by currency symbol (e.g., "$", "؋")

**Response (200 OK):**
```json
[
  {
    "id": 2,
    "code": "USD",
    "name": "US Dollar",
    "name_english": "US Dollar", 
    "name_farsi": "دالر آمریکا",
    "symbol": "$",
    "is_active": true,
    "is_default": true,
    "exchange_rate": "85.50"
  }
]
```

- **Get Currency Details**: `GET /api/currencies/{currency_id}/`

**Response (200 OK):**
```json
{
  "id": 1,
  "code": "AFN",
  "name": "Afghan Afghani",
  "name_english": "Afghan Afghani",
  "name_farsi": "افغانی افغانستان", 
  "symbol": "؋",
  "is_active": true,
  "is_default": false,
  "exchange_rate": "1.00"
}
```

- **Get Saraf Supported Currencies**: `GET /api/saraf-profile/{saraf_id}/supported-currencies/?is_active={true|false}`

**Query Parameters:**
- `is_active` (optional) - Filter by active status ("true", "false", "1", "0")

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "currency": {
      "id": 1,
      "code": "AFN", 
      "name": "Afghan Afghani",
      "symbol": "؋"
    },
    "created_at": "2024-01-15T10:00:00Z"
  }
]
```

### 8. Chat
- **Send Message**: `POST /api/messages/send/`

**Required Fields:**
- `receiver_id` - ID of message recipient
- `receiver_type` - Type of recipient ("saraf" or "normal_user")

**Optional Fields:**
- `content` - Text content of message
- `message_type` - Message type ("text", "attachment", "mixed") - defaults to "text"
- `attachment_files` - Array of file attachments

**Body:**
```json
{
  "receiver_id": 2,
  "receiver_type": "normal_user",
  "content": "Hello, how can I help you?",
  "message_type": "text",
  "attachment_files": []
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "sender_saraf": 1,
  "sender_normal_user": null,
  "receiver_saraf": null,
  "receiver_normal_user": 2,
  "message_type": "text",
  "content": "Hello, how can I help you?",
  "is_read": false,
  "is_deleted_by_sender": false,
  "is_deleted_by_receiver": false,
  "created_at": "2024-01-15T10:30:00Z",
  "read_at": null
}
```

- **List Messages**: `GET /api/messages/list/?user_type={user_type}&user_id={user_id}`

**Query Parameters:**
- `user_type` (required) - Type of other user ("saraf" or "normal_user")
- `user_id` (required) - ID of other user to get conversation with

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "sender_saraf": 1,
    "sender_normal_user": null,
    "receiver_saraf": null,
    "receiver_normal_user": 2,
    "message_type": "text",
    "content": "Hello, how can I help you?",
    "is_read": false,
    "is_deleted_by_sender": false,
    "is_deleted_by_receiver": false,
    "created_at": "2024-01-15T10:30:00Z",
    "read_at": null
  }
]
```

- **Mark Message as Read**: `POST /api/messages/{message_id}/mark-read/`

**Required Fields:**
- `message_id` (URL parameter) - ID of the message to mark as read

**Response (200 OK):**
```json
{
  "message": "Message marked as read"
}
```

- **List Conversations**: `GET /api/conversations/`

**Response (200 OK):**
```json
[
  {
    "participant_id": 2,
    "participant_type": "normal_user",
    "participant_name": "Omar Khan",
    "last_message": "Hello, how can I help you?",
    "last_message_time": "2024-01-15T10:30:00Z",
    "unread_count": 1
  }
]
```

### 9. Send Hawala
`POST /api/sendhawala/`

**Required Fields:**
- `hawala_number` - Unique hawala transaction number
- `sender_name` - Name of sender
- `receiver_name` - Name of receiver
- `amount` - Transaction amount
- `currency_code` - Currency code (e.g., "USD", "AFN")
- `receiver_location` - Receiver's location/province
- `exchanger_location` - Exchanger's location/province
- `sender_phone` - Sender's phone number

**Optional Fields:**
- `hawala_fee` - Transaction fee amount
- `hawala_fee_currency_code` - Fee currency code
- `status` - Transaction status ("draft", "pending", "finished")

**Body:**
```json
{
  "hawala_number": 12345,
  "sender_name": "Ahmad",
  "receiver_name": "Omar",
  "amount": 1000.0,
  "currency_code": "USD",
  "receiver_location": "Kabul",
  "exchanger_location": "Herat",
  "sender_phone": "0700123456",
  "hawala_fee": 50.0,
  "hawala_fee_currency_code": "USD",
  "status": "finished"
}
```

**Response (201 Created):**
```json
{
  "send_hawala_id": 1,
  "hawala_number": 12345,
  "sender_name": "Ahmad",
  "receiver_name": "Omar",
  "amount": "1000.00",
  "currency": {
    "id": 2,
    "code": "USD",
    "name": "US Dollar",
    "symbol": "$"
  },
  "receiver_location": "Kabul",
  "exchanger_location": "Herat",
  "sender_phone": "0700123456",
  "hawala_fee": "50.00",
  "hawala_fee_currency": {
    "id": 2,
    "code": "USD",
    "name": "US Dollar",
    "symbol": "$"
  },
  "status": "finished",
  "dates": "2024-01-15T10:30:00Z"
}
```

### 10. Receive Hawala
`POST /api/receive-hawala/create/`

**Description:** Create a new ReceiveHawala record by linking to existing sendhawala using hawala_number. This automatically copies all sendhawala details and adds receiver verification data.

**Required Fields:**
- `hawala_number` - Hawala number from existing sendhawala
- `receiver_phone` - Receiver's phone number
- `receiver_address` - Receiver's address

**Optional Fields:**
- `receiver_id_card_photo` - ID card photo (multipart/form-data)
- `receiver_finger_photo` - Fingerprint photo (multipart/form-data)

**Body:**
```json
{
  "hawala_number": 12345,
  "receiver_phone": "0700123456",
  "receiver_address": "Street 5, District 3, Kabul",
  "receiver_id_card_photo": "(file upload)",
  "receiver_finger_photo": "(file upload)"
}
```

**Response (201 Created):**
```json
{
  "message": "ReceiveHawala created successfully with sendhawala details",
  "data": {
    "id": 1,
    "sendhawala": 1,
    "hawala_number": "12345",
    "sender_name": "Ahmad",
    "receiver_name": "Omar",
    "amount": "1000.00",
    "currency": {
      "id": 2,
      "code": "USD",
      "name": "US Dollar",
      "symbol": "$"
    },
    "receiver_location": {
      "name": "Kabul"
    },
    "exchanger_location": {
      "name": "Herat"
    },
    "sender_phone": "0700123456",
    "hawala_fee": "50.00",
    "hawala_fee_currency": {
      "id": 2,
      "code": "USD",
      "name": "US Dollar",
      "symbol": "$"
    },
    "status": "finished",
    "dates": "2024-01-15T10:30:00Z",
    "receiver_phone": "0700123456",
    "receiver_address": "Street 5, District 3, Kabul",
    "receiver_id_card_photo": null,
    "receiver_finger_photo": null,
    "created_at": "2024-01-15T11:00:00Z",
    "verified_by": null,
    "verification_date": null,
    "sendhawala_details": {
      "send_hawala_id": 1,
      "hawala_number": 12345,
      "sender_name": "Ahmad",
      "receiver_name": "Omar",
      "amount": "1000.00",
      "currency": {
        "id": 2,
        "code": "USD",
        "name": "US Dollar",
        "symbol": "$"
      },
      "receiver_location": "Kabul",
      "exchanger_location": "Herat",
      "sender_phone": "0700123456",
      "hawala_fee": "50.00",
      "hawala_fee_currency": {
        "id": 2,
        "code": "USD",
        "name": "US Dollar",
        "symbol": "$"
      },
      "status": "finished",
      "created_at": "2024-01-15T10:30:00Z"
    }
  }
}
```

**Error Responses:**

**400 Bad Request - Invalid hawala_number:**
```json
{
  "hawala_number": ["No sendhawala found with hawala_number: 99999"]
}
```

**400 Bad Request - Duplicate ReceiveHawala:**
```json
{
  "error": "Validation error",
  "details": {
    "hawala_number": "ReceiveHawala already exists for hawala_number: 12345"
  }
}
```

**400 Bad Request - Missing required fields:**
```json
{
  "receiver_phone": ["receiver_phone is required"],
  "receiver_address": ["receiver_address is required"]
}
```

**401 Unauthorized:**
```json
{
  "error": "Authentication required. Please login first."
}
```

### 11. Currency Price
- **Get Latest Rates**: `GET /api/currency/latest/`

**Response (200 OK):**
```json
[
  {
    "currency_code": "USD",
    "rate": 85.50,
    "last_updated": "2024-01-15T10:00:00Z"
  },
  {
    "currency_code": "EUR",
    "rate": 92.30,
    "last_updated": "2024-01-15T10:00:00Z"
  }
]
```

- **Get Specific Rate**: `GET /api/currency/rate/{currency_code}/`

**Response (200 OK):**
```json
{
  "currency_code": "USD",
  "rate": 85.50,
  "last_updated": "2024-01-15T10:00:00Z"
}
```

### 12. Colleague and Functions
- **List Colleagues**: `GET /api/colleagues/`

**Query Parameters:**
- `status` (optional) - Filter by colleague status ("delivered", "undelivered")

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "requester": 1,
    "colleague": 2,
    "requester_name": "Ahmadi Exchange",
    "colleague_name": "Khan Exchange",
    "requester_details": {
      "saraf_id": 1,
      "exchange_name": "Ahmadi Exchange",
      "phone": "0700123456",
      "email": "ali@example.com"
    },
    "colleague_details": {
      "saraf_id": 2,
      "exchange_name": "Khan Exchange",
      "phone": "0700123458",
      "email": "ahmad@example.com"
    },
    "status": "delivered",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

- **Add Colleague**: `POST /api/colleagues/add/`

**Required Fields:**
- `colleague` - ID of the saraf to add as colleague

**Optional Fields:**
- `status` - Colleague status ("delivered", "undelivered") - defaults to "undelivered"

**Body:**
```json
{
  "colleague": 2,
  "status": "delivered"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "requester": 1,
  "colleague": 2,
  "requester_name": "Ahmadi Exchange",
  "colleague_name": "Khan Exchange",
  "status": "delivered",
  "created_at": "2024-01-15T10:30:00Z"
}
```

- **Get Colleague Detail**: `GET /api/colleagues/{saraf_id}/`

**Note:** Use the saraf_id of the colleague, not the relationship ID.

**Response (200 OK):**
```json
{
  "id": 1,
  "requester": 1,
  "colleague": 2,
  "requester_name": "Ahmadi Exchange",
  "colleague_name": "Khan Exchange",
  "requester_details": {
    "saraf_id": 1,
    "exchange_name": "Ahmadi Exchange",
    "phone": "0700123456",
    "email": "ali@example.com"
  },
  "colleague_details": {
    "saraf_id": 2,
    "exchange_name": "Khan Exchange",
    "phone": "0700123458",
    "email": "ahmad@example.com"
  },
  "status": "delivered",
  "created_at": "2024-01-15T10:30:00Z"
}
```

- **Update Colleague Status**: `PATCH /api/colleagues/{saraf_id}/`

**Note:** Use the saraf_id of the colleague, not the relationship ID.

**Required Fields:**
- `status` - New status ("delivered", "undelivered")

**Body:**
```json
{
  "status": "undelivered"
}
```

**Response (200 OK):**
```json
{
  "message": "Colleague status updated to undelivered",
  "data": {
    "id": 1,
    "requester": 1,
    "colleague": 2,
    "requester_name": "Ahmadi Exchange",
    "colleague_name": "Khan Exchange",
    "status": "undelivered",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### 13. Loans Management
- **List Loans**: `GET /api/loans/`

**Query Parameters:**
- `status` (optional) - Filter by loan status ("active", "repaid", "defaulted")
- `role` (optional) - Filter by user role ("lender", "borrower")

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "lender": 1,
    "borrower": 2,
    "lender_name": "Ahmadi Exchange",
    "borrower_name": "Khan Exchange",
    "amount": "5000.00",
    "currency": {
      "id": 2,
      "code": "USD",
      "name": "US Dollar",
      "symbol": "$"
    },
    "interest_rate": "5.00",
    "duration_months": 12,
    "status": "active",
    "loan_date": "2024-01-15T10:30:00Z",
    "due_date": "2025-01-15T10:30:00Z"
  }
]
```

- **Create Loan**: `POST /api/loans/create/`

**Required Fields:**
- `borrower` - ID of the borrowing saraf
- `amount` - Loan amount
- `currency_code` - Currency code (e.g., "USD", "AFN")

**Optional Fields:**
- `description` - Loan description
- `status` - Loan status ("delivered", "undelivered") - defaults to "undelivered"

**Body:**
```json
{
  "borrower": 2,
  "amount": 5000.00,
  "currency_code": "USD",
  "description": "Business expansion loan"
}
```

**Example with minimal required fields:**
```json
{
  "borrower": 2,
  "amount": 1000.00,
  "currency_code": "AFN"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "lender": 1,
  "borrower": 2,
  "lender_name": "Ahmadi Exchange",
  "borrower_name": "Khan Exchange",
  "amount": "5000.00",
  "currency": {
    "id": 2,
    "code": "USD",
    "name": "US Dollar",
    "symbol": "$"
  },
  "interest_rate": "5.00",
  "duration_months": 12,
  "status": "active",
  "description": "Business expansion loan",
  "loan_date": "2024-01-15T10:30:00Z",
  "due_date": "2025-01-15T10:30:00Z"
}
```

- **Get Loan Detail**: `GET /api/loans/{id}/`

**Response (200 OK):**
```json
{
  "id": 1,
  "lender": 1,
  "borrower": 2,
  "lender_name": "Ahmadi Exchange",
  "borrower_name": "Khan Exchange",
  "amount": "5000.00",
  "currency": {
    "id": 2,
    "code": "USD",
    "name": "US Dollar",
    "symbol": "$"
  },
  "interest_rate": "5.00",
  "duration_months": 12,
  "status": "active",
  "description": "Business expansion loan",
  "loan_date": "2024-01-15T10:30:00Z",
  "due_date": "2025-01-15T10:30:00Z"
}
```

### 14. Currency Exchange Management
- **List Exchanges**: `GET /api/exchanges/`

**Query Parameters:**
- `status` (optional) - Filter by exchange status ("delivered", "undelivered")
- `role` (optional) - Filter by user role ("exchanger", "receiver")

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "exchanger": 1,
    "receiver": 2,
    "exchanger_name": "Ahmadi Exchange",
    "receiver_name": "Khan Exchange",
    "from_currency": 2,
    "to_currency": 1,
    "from_currency_details": {
      "id": 2,
      "code": "USD",
      "name": "US Dollar",
      "symbol": "$"
    },
    "to_currency_details": {
      "id": 1,
      "code": "AFN",
      "name": "Afghan Afghani",
      "symbol": "؋"
    },
    "amount": "100.00",
    "rate": "85.500000",
    "converted_amount": "8550.00",
    "status": "delivered",
    "description": "Currency exchange for business",
    "date": "2024-01-15T10:30:00Z"
  }
]
```

- **Create Exchange**: `POST /api/exchanges/create/`

**Required Fields:**
- `receiver` - ID of the receiving saraf
- `from_currency_code` - Source currency code
- `to_currency_code` - Target currency code
- `amount` - Amount to exchange
- `rate` - Exchange rate

**Optional Fields:**
- `description` - Exchange description
- `status` - Exchange status ("delivered", "undelivered") - defaults to "undelivered"

**Body:**
```json
{
  "receiver": 2,
  "from_currency_code": "USD",
  "to_currency_code": "AFN",
  "amount": 100.00,
  "rate": 85.50,
  "description": "Currency exchange for business",
  "status": "delivered"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "exchanger": 1,
  "receiver": 2,
  "exchanger_name": "Ahmadi Exchange",
  "receiver_name": "Khan Exchange",
  "from_currency": 2,
  "to_currency": 1,
  "from_currency_details": {
    "id": 2,
    "code": "USD",
    "name": "US Dollar",
    "symbol": "$"
  },
  "to_currency_details": {
    "id": 1,
    "code": "AFN",
    "name": "Afghan Afghani",
    "symbol": "؋"
  },
  "amount": "100.00",
  "rate": "85.500000",
  "converted_amount": "8550.00",
  "status": "delivered",
  "description": "Currency exchange for business",
  "date": "2024-01-15T10:30:00Z"
}
```

- **Get Exchange Detail**: `GET /api/exchanges/{id}/`

**Response (200 OK):**
```json
{
  "id": 1,
  "exchanger": 1,
  "receiver": 2,
  "exchanger_name": "Ahmadi Exchange",
  "receiver_name": "Khan Exchange",
  "from_currency": 2,
  "to_currency": 1,
  "from_currency_details": {
    "id": 2,
    "code": "USD",
    "name": "US Dollar",
    "symbol": "$"
  },
  "to_currency_details": {
    "id": 1,
    "code": "AFN",
    "name": "Afghan Afghani",
    "symbol": "؋"
  },
  "amount": "100.00",
  "rate": "85.500000",
  "converted_amount": "8550.00",
  "status": "delivered",
  "description": "Currency exchange for business",
  "date": "2024-01-15T10:30:00Z"
}
```

### 15. Customers and Functions
- **List Customers**: `GET /api/customer-account/list/`

**Query Parameters:**
- `is_active` (optional) - Filter by active status ("true", "false")
- `search` (optional) - Search by name, phone, or account number

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "account_number": "ACC001",
    "full_name": "Omar Ali",
    "saraf": 1,
    "saraf_name": "Ahmadi Exchange",
    "phone": "0700123459",
    "address": "Street 10, District 5, Kabul",
    "job": "Teacher",
    "balance": "500.00",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "balances": [
      {
        "currency": {
          "id": 2,
          "name": "US Dollar",
          "code": "USD",
          "symbol": "$"
        },
        "balance": "500.00",
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ]
  }
]
```

- **Create Customer**: `POST /api/customer-account/create/`

**Required Fields:**
- `account_number` - Unique account number
- `full_name` - Customer's full name
- `saraf` - ID of the saraf
- `phone` - Customer's phone number
- `address` - Customer's address

**Optional Fields:**
- `job` - Customer's job/profession
- `finger_photo` - Fingerprint photo (multipart/form-data)
- `photo` - Customer photo (multipart/form-data)

**Body:**
```json
{
  "account_number": "ACC001",
  "full_name": "Omar Ali",
  "saraf": 1,
  "phone": "0700123459",
  "address": "Street 10, District 5, Kabul",
  "job": "Teacher"
}
```

**Note:** For file uploads (finger_photo, photo), use multipart/form-data format.

**Response (201 Created):**
```json
{
  "id": 1,
  "account_number": "ACC001",
  "full_name": "Omar Ali",
  "saraf": 1,
  "saraf_name": "Ahmadi Exchange",
  "phone": "0700123459",
  "address": "Street 10, District 5, Kabul",
  "job": "Teacher",
  "balance": "0.00",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "balances": []
}
```

### 14. Currency Exchange

---

**Query Parameters:**
- `status` (required) - Filter by status ("draft", "pending", "finished")

**Response (200 OK):**
```json
[
  {
    "send_hawala_id": 1,
    "hawala_number": 12345,
    "sender_name": "Ahmad",
    "receiver_name": "Omar",
    "amount": "1000.00",
    "currency": {
      "id": 2,
      "code": "USD",
      "name": "US Dollar",
      "symbol": "$"
    },
    "receiver_location": "Kabul",
    "exchanger_location": "Herat",
    "sender_phone": "0700123456",
    "hawala_fee": "50.00",
    "status": "finished",
    "dates": "2024-01-15T10:30:00Z"
  }
]
```

---

## 👤 Normal User APIs

### 1. Create Normal User Account
`POST /api/normal-user-profile/create/`

**Required Fields:**
- `name` - First name
- `last_name` - Last name
- `phone` - Phone number
- `email` - Email address
- `password` - Password

**Optional Fields:**
- `preferred_currency_id` - ID of preferred currency

**Body:**
```json
{
  "name": "Omar",
  "last_name": "Khan",
  "phone": "0700123457",
  "email": "omar@example.com",
  "password": "Pass123!",
  "preferred_currency_id": 1
}
```

**Response (201 Created):**
```json
{
  "normal_user_id": 1,
  "name": "Omar",
  "last_name": "Khan",
  "phone": "0700123457",
  "email": "omar@example.com",
  "preferred_currency": {
    "id": 1,
    "code": "AFN",
    "name": "Afghan Afghani",
    "symbol": "؋"
  },
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

### 2. Normal User Login
`POST /api/normal-user-profile/login/`

**Required Fields:**
- `email` - Email address
- `password` - Password

**Body:**
```json
{
  "email": "omar@example.com",
  "password": "Pass123!"
}
```

**Response (200 OK):**
```json
{
  "message": "Login successful",
  "normal_user_id": 1,
  "name": "Omar",
  "session_id": "xyz789abc123"
}
```

### 3. Normal User Logout
`POST /api/logout/`

**Response (200 OK):**
```json
{
  "message": "Logout successful"
}
```

### 4. Change Normal User Password
`POST /api/normal-user-profile/{user_id}/change-password/`

**Required Fields:**
- `old_password` - Current password
- `new_password` - New password
- `new_password_confirm` - New password confirmation

**Body:**
```json
{
  "old_password": "Pass123!",
  "new_password": "NewPass456!",
  "new_password_confirm": "NewPass456!"
}
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

### 5. Update Normal User Logo
`PUT /api/normal-user-profile/{normal_user_id}/update-user-logo/`

**Required Fields:**
- `user_logo` - Image file (multipart/form-data)

**Body (multipart/form-data):**
```
user_logo: (file upload)
```

**Response (200 OK):**
```json
{
  "message": "user_logo updated",
  "normal_user_id": 1
}
```

### 6. Update Normal User Wallpaper
`PUT /api/normal-user-profile/{normal_user_id}/update-user-wallpaper/`

**Required Fields:**
- `user_wallpaper` - Image file (multipart/form-data)

**Body (multipart/form-data):**
```
user_wallpaper: (file upload)
```

**Response (200 OK):**
```json
{
  "message": "user_wallpaper updated",
  "normal_user_id": 1
}
```

### 7. Update Multiple Normal User Photos
`PUT /api/normal-user-profile/{normal_user_id}/update-photos/`

**Optional Fields (at least one required):**
- `user_logo` - Logo/avatar image file
- `user_wallpaper` - Wallpaper/background image file

**Body (multipart/form-data):**
```
user_logo: (file upload)
user_wallpaper: (file upload)
```

**Response (200 OK):**
```json
{
  "message": "Photos updated successfully",
  "updated_fields": ["user_logo", "user_wallpaper"],
  "data": {
    "normal_user_id": 1,
    "name": "Omar",
    "last_name": "Khan",
    "phone": "0700123457",
    "email": "omar@example.com",
    "user_logo": "/media/normal_user_photos/logo.jpg",
    "user_wallpaper": "/media/normal_user_photos/wallpaper.jpg",
    "preferred_currency": {
      "id": 1,
      "code": "AFN",
      "name": "Afghan Afghani",
      "symbol": "؋"
    },
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z"
  }
}
```

### 8. Delete Normal User Account
`DELETE /api/normal-user-profile/{user_id}/`

**Response (200 OK):**
```json
{
  "message": "Account deleted successfully"
}
```

### 6. Province
- **List Provinces**: `GET /api/provinces/`

**Response (200 OK):**
```json
[
  {
    "name": "Kabul"
  },
  {
    "name": "Herat"
  }
]
```

### 7. Currency
- **List Currencies**: `GET /api/currencies/`

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "code": "AFN",
    "name": "Afghan Afghani",
    "symbol": "؋"
  },
  {
    "id": 2,
    "code": "USD",
    "name": "US Dollar",
    "symbol": "$"
  }
]
```

- **List Currencies with Filters**: `GET /api/currencies/?code={currency_code}&symbol={symbol}`

**Query Parameters:**
- `code` (optional) - Filter by currency code (e.g., "USD", "AFN")
- `symbol` (optional) - Filter by currency symbol (e.g., "$", "؋")

**Response (200 OK):**
```json
[
  {
    "id": 2,
    "code": "USD",
    "name": "US Dollar",
    "name_english": "US Dollar", 
    "name_farsi": "دالر آمریکا",
    "symbol": "$",
    "is_active": true,
    "is_default": true,
    "exchange_rate": "85.50"
  }
]
```

- **Get Currency Details**: `GET /api/currencies/{currency_id}/`

**Response (200 OK):**
```json
{
  "id": 1,
  "code": "AFN",
  "name": "Afghan Afghani",
  "name_english": "Afghan Afghani",
  "name_farsi": "افغانی افغانستان", 
  "symbol": "؋",
  "is_active": true,
  "is_default": false,
  "exchange_rate": "1.00"
}
```

- **Get Saraf Supported Currencies**: `GET /api/saraf-profile/{saraf_id}/supported-currencies/?is_active={true|false}`

**Query Parameters:**
- `is_active` (optional) - Filter by active status ("true", "false", "1", "0")

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "currency": {
      "id": 1,
      "code": "AFN", 
      "name": "Afghan Afghani",
      "symbol": "؋"
    },
    "created_at": "2024-01-15T10:00:00Z"
  }
]
```

### 8. Chat
- **Send Message**: `POST /api/messages/send/`

**Required Fields:**
- `receiver_id` - ID of message recipient
- `receiver_type` - Type of recipient ("saraf" or "normal_user")

**Optional Fields:**
- `content` - Text content of message
- `message_type` - Message type ("text", "attachment", "mixed") - defaults to "text"
- `attachment_files` - Array of file attachments

**Body:**
```json
{
  "receiver_id": 1,
  "receiver_type": "saraf",
  "content": "I need help with a transaction",
  "message_type": "text",
  "attachment_files": []
}
```

**Response (201 Created):**
```json
{
  "id": 2,
  "sender_saraf": null,
  "sender_normal_user": 1,
  "receiver_saraf": 1,
  "receiver_normal_user": null,
  "message_type": "text",
  "content": "I need help with a transaction",
  "is_read": false,
  "is_deleted_by_sender": false,
  "is_deleted_by_receiver": false,
  "created_at": "2024-01-15T11:00:00Z",
  "read_at": null
}
```

- **List Messages**: `GET /api/messages/list/?user_type={user_type}&user_id={user_id}`

**Query Parameters:**
- `user_type` (required) - Type of other user ("saraf" or "normal_user")
- `user_id` (required) - ID of other user to get conversation with

**Response (200 OK):**
```json
[
  {
    "id": 2,
    "sender_saraf": null,
    "sender_normal_user": 1,
    "receiver_saraf": 1,
    "receiver_normal_user": null,
    "message_type": "text",
    "content": "I need help with a transaction",
    "is_read": false,
    "is_deleted_by_sender": false,
    "is_deleted_by_receiver": false,
    "created_at": "2024-01-15T11:00:00Z",
    "read_at": null
  }
]
```

### 9. Send Hawala
`POST /api/sendhawala/`

**Required Fields:**
- `hawala_number` - Unique hawala transaction number
- `sender_name` - Name of sender
- `receiver_name` - Name of receiver
- `amount` - Transaction amount
- `currency_code` - Currency code (e.g., "USD", "AFN")
- `receiver_location` - Receiver's location/province
- `exchanger_location` - Exchanger's location/province
- `sender_phone` - Sender's phone number

**Optional Fields:**
- `hawala_fee` - Transaction fee amount
- `hawala_fee_currency_code` - Fee currency code
- `status` - Transaction status ("draft", "pending", "finished")

**Body:**
```json
{
  "hawala_number": 12346,
  "sender_name": "Omar",
  "receiver_name": "Ahmad",
  "amount": 500.0,
  "currency_code": "USD",
  "receiver_location": "Herat",
  "exchanger_location": "Kabul",
  "sender_phone": "0700123457",
  "hawala_fee": 25.0,
  "hawala_fee_currency_code": "USD",
  "status": "finished"
}
```

**Response (201 Created):**
```json
{
  "send_hawala_id": 2,
  "hawala_number": 12346,
  "sender_name": "Omar",
  "receiver_name": "Ahmad",
  "amount": "500.00",
  "currency": {
    "id": 2,
    "code": "USD",
    "name": "US Dollar",
    "symbol": "$"
  },
  "receiver_location": "Herat",
  "exchanger_location": "Kabul",
  "sender_phone": "0700123457",
  "hawala_fee": "25.00",
  "hawala_fee_currency": {
    "id": 2,
    "code": "USD",
    "name": "US Dollar",
    "symbol": "$"
  },
  "status": "finished",
  "dates": "2024-01-15T11:30:00Z"
}
```

### 10. Receive Hawala
`POST /api/receive-hawala/create/`

**Required Fields:**
- `sendhawala` - ID of the send hawala transaction
- `receiver_phone` - Receiver's phone number
- `receiver_address` - Receiver's address

**Optional Fields:**
- `receiver_id_card_photo` - ID card photo (multipart/form-data)
- `receiver_finger_photo` - Fingerprint photo (multipart/form-data)

**Body:**
```json
{
  "sendhawala": 2,
  "receiver_phone": "0700123457",
  "receiver_address": "Street 8, District 2, Herat",
  "receiver_id_card_photo": "(file upload)",
  "receiver_finger_photo": "(file upload)"
}
```

**Response (201 Created):**
```json
{
  "id": 2,
  "sendhawala": 2,
  "hawala_number": "12346",
  "sender_name": "Omar",
  "receiver_name": "Ahmad",
  "amount": "500.00",
  "currency": {
    "id": 2,
    "code": "USD",
    "name": "US Dollar"
  },
  "receiver_location": {
    "name": "Herat"
  },
  "exchanger_location": {
    "name": "Kabul"
  },
  "sender_phone": "0700123457",
  "hawala_fee": "25.00",
  "hawala_fee_currency": {
    "id": 2,
    "code": "USD",
    "name": "US Dollar"
  },
  "status": "draft",
  "dates": "2024-01-15T11:30:00Z",
  "receiver_phone": "0700123457",
  "receiver_address": "Street 8, District 2, Herat",
  "created_at": "2024-01-15T12:00:00Z"
}
```

### 11. Currency Price
- **Get Latest Rates**: `GET /api/currency/latest/`

**Response (200 OK):**
```json
[
  {
    "currency_code": "USD",
    "rate": 85.50,
    "last_updated": "2024-01-15T10:00:00Z"
  },
  {
    "currency_code": "EUR",
    "rate": 92.30,
    "last_updated": "2024-01-15T10:00:00Z"
  }
]
```

### 12. Colleague and Functions
*Not applicable for Normal Users.*

### 13. Customers and Functions
*Not applicable for Normal Users.*

### 14. Currency Exchange
*Not applicable for Normal Users.*

---

## 🔗 Additional API Endpoints

### 15. Colleague Management (Saraf Only)

- **Add Colleague**: `POST /api/colleagues/add/`

**Required Fields:**
- `colleague_saraf_id` - ID of the colleague saraf
- `relationship_type` - Type of relationship ("partner", "agent", "branch")

**Optional Fields:**
- `notes` - Additional notes about the relationship

**Response (201 Created):**
```json
{
  "id": 1,
  "saraf": 1,
  "colleague_saraf": 2,
  "relationship_type": "partner",
  "notes": "Main business partner",
  "created_at": "2024-01-15T10:30:00Z",
  "is_active": true
}
```

- **Get Colleague Details**: `GET /api/colleagues/{colleague_id}/`

**Response (200 OK):**
```json
{
  "id": 1,
  "saraf": 1,
  "colleague_saraf": 2,
  "relationship_type": "partner",
  "notes": "Main business partner",
  "created_at": "2024-01-15T10:30:00Z",
  "is_active": true
}
```

### 16. Loan Management (Saraf Only)

- **Create Loan**: `POST /api/loans/create/`

**Required Fields:**
- `borrower_name` - Name of the borrower
- `amount` - Loan amount
- `currency` - Currency ID
- `interest_rate` - Interest rate percentage
- `duration_months` - Loan duration in months

**Optional Fields:**
- `collateral_description` - Description of collateral
- `purpose` - Purpose of the loan

**Response (201 Created):**
```json
{
  "id": 1,
  "saraf": 1,
  "borrower_name": "Ahmad Khan",
  "amount": "5000.00",
  "currency": 1,
  "interest_rate": "5.50",
  "duration_months": 12,
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z",
  "due_date": "2025-01-15T10:30:00Z"
}
```

- **Get Loan Details**: `GET /api/loans/{loan_id}/`

**Response (200 OK):**
```json
{
  "id": 1,
  "saraf": 1,
  "borrower_name": "Ahmad Khan",
  "amount": "5000.00",
  "currency": 1,
  "interest_rate": "5.50",
  "duration_months": 12,
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z",
  "due_date": "2025-01-15T10:30:00Z"
}
```
### 24. Send Hawala Filter
`GET /api/send-hawala/filter/?status={status}`

### 17. Receive Hawala Management

- **List Receive Hawala**: `GET /api/receive-hawala/list/`

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "hawala_number": "RH001234",
    "sender_name": "Omar Khan",
    "receiver_name": "Ahmad Ali",
    "amount": "1000.00",
    "currency": "USD",
    "status": "pending",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

- **Get Receive Hawala Details**: `GET /api/receive-hawala/{id}/`

**Response (200 OK):**
```json
{
  "id": 1,
  "hawala_number": "RH001234",
  "sender_name": "Omar Khan",
  "receiver_name": "Ahmad Ali",
  "amount": "1000.00",
  "currency": "USD",
  "status": "pending",
  "created_at": "2024-01-15T10:30:00Z",
  "verified_at": null
}
```

- **Verify Receive Hawala**: `POST /api/receive-hawala/{id}/verify/`

**Response (200 OK):**
```json
{
  "message": "Hawala verified successfully",
  "hawala_id": 1,
  "verified_at": "2024-01-15T11:00:00Z"
}
```

### 18. Saraf Profile Management

- **List All Sarfs**: `GET /api/saraf-profile/list/`

**Response (200 OK):**
```json
[
  {
    "saraf_id": 1,
    "saraf_name": "Khan Exchange",
    "phone_number": "+93701234567",
    "email": "khan@exchange.com",
    "province": "Kabul",
    "is_active": true
  }
]
```

- **Get Saraf Details**: `GET /api/saraf-profile/{saraf_id}/`

**Response (200 OK):**
```json
{
  "saraf_id": 1,
  "saraf_name": "Khan Exchange",
  "phone_number": "+93701234567",
  "email": "khan@exchange.com",
  "province": "Kabul",
  "address": "Main Street, Kabul",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 19. Normal User Profile Management

- **List All Normal Users**: `GET /api/normal-user-profile/list/`

**Response (200 OK):**
```json
[
  {
    "normal_user_id": 1,
    "name": "Ahmad Ali",
    "phone_number": "+93701234567",
    "email": "ahmad@example.com",
    "province": "Herat",
    "is_active": true
  }
]
```

- **Get Normal User Details**: `GET /api/normal-user-profile/{normal_user_id}/`

**Response (200 OK):**
```json
{
  "normal_user_id": 1,
  "name": "Ahmad Ali",
  "phone_number": "+93701234567",
  "email": "ahmad@example.com",
  "province": "Herat",
  "address": "City Center, Herat",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 20. Province and Currency Details

- **Get Province Details**: `GET /api/provinces/{province_name}/`

**Response (200 OK):**
```json
{
  "province_name": "Kabul",
  "province_name_english": "Kabul",
  "province_name_farsi": "کابل"
}
```

- **Get Currency Details**: `GET /api/currencies/{currency_id}/`

**Response (200 OK):**
```json
{
  "id": 1,
  "code": "AFN",
  "name": "Afghan Afghani",
  "name_english": "Afghan Afghani",
  "name_farsi": "افغانی افغانستان",
  "symbol": "؋",
  "is_active": true,
  "is_default": false,
  "exchange_rate": "1.00"
}
```
