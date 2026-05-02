

## **Project Title: Nashville Metro Insights Platform**

### **Executive Summary**

This project aims to create a unified analytics platform to understand complex urban dynamics within the Metro Nashville area. By ingesting and integrating **housing data, 311 service requests, public safety reports, and census data**, we can uncover key trends, correlations, and anomalies. The platform utilizes a modern, scalable data stack to provide city planners, public safety officials, and other stakeholders with actionable insights through interactive dashboards and a flexible API. The core objective is to move from siloed data to a centralized, reliable source of truth for data-driven decision-making.

---

### **Data Sources**

* **Nashville Housing Data:** Real estate transaction records, prices, and property characteristics.  
* **Nashville 311 Data:** Non-emergency service requests from citizens (e.g., pothole reports, trash collection issues).  
* **Public Safety Data:** Aggregated and anonymized incident reports.  
* **U.S. Census Data:** Demographic and economic data for Davidson County and surrounding areas.

---

### **Technical Architecture**

The architecture is designed to be modular and scalable, using a combination of open-source tools to create an end-to-end data pipeline. Data flows from raw storage to a semantic layer, making it accessible for various downstream uses.

| Technology | Role in Project | Purpose |
| :---- | :---- | :---- |
| **Custom Scripts (Python)** | Data Ingestion | Extract data from various sources and load it into raw storage. |
| **MinIO** | Raw Data Lake | Stores the initial, unmodified JSON files from the ingestion scripts. |
| **DuckDB** | Analytical Engine | Acts as the high-performance query engine for transformations and views. |
| **SQLMesh** | Data Transformation | Manages the ELT process, converting raw JSON to a Parquet **Bronze Layer**, handling all subsequent transformations (**Silver/Gold Layers**), and running data quality tests. |
| **Prefect** | Orchestration | Automates and schedules the entire data pipeline, from ingestion to transformation. |
| **Cube.js** | Semantic Layer & API | Defines business logic, metrics, and joins. Provides a consistent, secure API for all data consumers. |
| **Metabase** | BI & Visualization | Connects to the Cube.js API to create and display interactive dashboards and reports for end-users. 📊 |

---

### **Project Workflow**

1. **Automated Ingestion:** **Prefect** triggers custom Python scripts on a schedule to fetch the latest data from all sources. These scripts land the raw JSON data into a **MinIO** bucket.  
2. **Bronze Layer Creation:** A **SQLMesh** model, also orchestrated by Prefect, reads the new JSON files from MinIO. It unnests the data and saves it in the efficient **Parquet** format, creating the Bronze layer. These tables are registered as views in **DuckDB**.  
3. **Transformation and Modeling:** Additional SQLMesh models perform cleaning, joining, and aggregation to create Silver (clean) and Gold (business-ready) layers. For example, 311 data is joined with census tract data to analyze service requests by demographic area. All transformations include data quality tests managed by SQLMesh.  
4. **Semantic Definition:** **Cube.js** connects to the DuckDB views. Here, we define key business metrics like average\_housing\_price\_per\_sqft or service\_requests\_per\_capita. This ensures all stakeholders and tools use the same definitions.  
5. **Data Delivery:**  
   * **Metabase** connects to the Cube.js API, allowing analysts to build dashboards without writing complex SQL.  
   * The **Cube.js API** is also available for direct queries from other applications or for data science teams.

   ### **Actionable Insights for Stakeholders**

This platform empowers stakeholders by revealing critical insights hidden within the combined data:

* **For City Planners:** The data provides a direct view into the relationship between housing market dynamics and infrastructure demand. It can identify neighborhoods where rapid property value growth correlates with a surge in 311 requests, enabling proactive infrastructure planning and more accurate budget allocation.   
* **For Public Safety Officials:** The platform can highlight correlations between specific types of public safety incidents and socio-economic factors derived from housing and census data. This allows for the development of data-informed patrol strategies and community engagement programs aimed at addressing root causes.   
* **For Community Organizations:** The data can quantify community needs by pinpointing geographic areas with a high concentration of service requests (e.g., code violations, sanitation issues) relative to their population. This empowers organizations to deploy resources more effectively and advocate for underserved communities with concrete evidence.

