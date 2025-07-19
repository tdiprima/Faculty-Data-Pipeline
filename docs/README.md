This main URL ([https://product-help.interfolio.com/en\_US/technical-resources/about-interfolio-apis-and-documentation](https://product-help.interfolio.com/en_US/technical-resources/about-interfolio-apis-and-documentation)) serves as an overview of Interfolio's APIs and technical documentation. I've reviewed the structure of Interfolio's help center. Interfolio's APIs are divided by product/module, and the one most relevant to your query is the **Faculty Activity Reporting (FAR) API** — also known as the Faculty180 API 📊. This API is designed for tasks like retrieving lists of faculty/users, pulling biographical information (e.g., profiles, vitae, activities, and other bio-related data), and integrating with external systems 🔗.

I'll explain the relevant URLs below, including how to navigate to them from the main page and why they're useful for your specific needs (getting faculty lists and bio info). These are direct links to sub-pages under the main URL you referenced. Note that Interfolio's documentation requires an account/login for full access 🔐, and API usage often needs institutional credentials or an API key (which is covered in the docs).

---

### 🔑 Key Relevant URL(s) for Faculty180 API

---

1. **Main Faculty Activity Reporting (FAR) API Documentation Page**

   * **Search**: `faculty activity reporting technical documentation/faculty activity reporting api`
   * **Navigation**: From the main URL, scroll down or search for "Faculty Activity Reporting API" under the APIs section.
   * **Why this matters**:
     This is your launchpad 🚀 for everything Faculty180 API. It includes:

     * 🔐 **Authentication and Setup**: How to get started with API keys, OAuth, and institutional access.
     * 🧭 **Endpoints Overview**: Available API calls like `/users` and `/faculty`.
     * 🧪 **General Usage**: Examples in Python, cURL, etc.

     **For your use case**:

     * 📋 **List faculty**: `GET /users` endpoint (with filters for dept, role, status).
     * 🧬 **Pull bio data**: `GET /users/{user_id}/vita`, `/activities`, or `/profiles`.

---

2. **API Endpoints and Schema Details**

   * **Search**: `faculty activity reporting technical documentation/faculty activity reporting api endpoints`
   * **Navigation**: Click on "API Endpoints" or "Schema" in the sidebar.
   * **Why this matters**:

     * 🧩 Specific endpoint info: URLs, parameters, and JSON formats.
     * 📦 Examples: `GET /users?unit_id={unit_id}&limit=100`, `GET /vitae/{vita_id}`
     * ⚠️ Covers error handling, rate limits, and querying best practices.

---

3. **FAR API Authentication and Best Practices**

   * **Search**: `faculty activity reporting technical documentation/faculty activity reporting api authentication`
   * **Navigation**: From the FAR API page, look for "Authentication."
   * **Why this matters**:

     * 🛡️ OAuth 2.0 flows, API keys, and access scopes.
     * 👥 Crucial for admins to prevent access errors and stay secure.

---

4. **Additional Resources for Data Integration (e.g., Bulk Exports)**

   * **Search**: `faculty activity reporting technical documentation/faculty activity reporting data integration`
   * **Navigation**: Search "Data Integration" from the main page or follow links under "Technical Documentation."
   * **Why this matters**:

     * 🏗️ Bulk pulls of bio info (like SFTP, webhooks, or syncing via API).
     * 📤 Great for generating full faculty data feeds.

---

### 📎 Additional Notes

* **Why Faculty180/FAR API?**
  Interfolio has other APIs (Faculty Search, Review, Tenure) 🎓 but Faculty180 is **the** API for activity data like CVs and bios.

* **Examples and Tutorials**
  🧠 Code samples are included in docs — search for "users endpoint" or "vitae export."

* **If This Isn't What You Need**
  😕 Looking for a different product like Dossier or ByCommittee? Check the API overview or reach out to support.

* **Access and Updates**
  🔄 URLs may change. Use the search bar on the help site if something's missing.

* **Limitations**
  🚧 Access is typically restricted (e.g., to IT admins), and there are rate limits 📉 and privacy laws (FERPA ⚖️) to consider.

---

The main Faculty Activity Reporting (FAR) API documentation page for Interfolio/Faculty 180 is not explicitly listed in the references. However, documentation is available upon request 📩 during the sales process. For access, contact Interfolio support at [help@interfolio.com](mailto:help@interfolio.com) or visit [https://product-help.interfolio.com](https://product-help.interfolio.com).

<br>
