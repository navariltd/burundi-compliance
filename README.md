# <center>Burundi Compliance</center>


## <center> OBR Integration for ERPNext</center>

 

### Overview

The Burundi Compliance app integrates OBR tax functionalities into ERPNext, enabling users to manage tax compliance efficiently.

### Installation

#### Manual Installation

1. [Install bench](https://github.com/frappe/bench)
2. [Install ERPNext](https://github.com/frappe/erpnext#installation)

3. Once bench and ERPNext are installed, add burundi_compliance to your bench by running:

```sh

$ bench get-app --branch {branch-name}  https://github.com/navariltd/burundi_compliance.git

```

Replace `{branch-name}` with the desired branch name from the repository. Ensure compatibility with your installed versions of Frappe and ERPNext.

4. Install the burundi_compliance app on your site by running:

```sh

$ bench --site {sitename}  install-app  burundi_compliance

```

Replace `{sitename}` with the name of your site.

  

### Troubleshooting

- If you encounter any errors during installation, refer to the error messages for guidance.

- Ensure all dependencies are correctly installed and compatible with the versions specified.

  
  
  
  ## Key Features
  1.[Setup](#setup)
  2.[Stock Movement](#Stock_Movement)
  3.[Selling](#Selling)

### <a id="setup"></a> 1. Setup
I believe we can see a Burundi Compliance module when we log into the system.
It has a workspace with three doctypes.

#### Doctypes
1. [eBMS Settings](#ebms_setting)
2. [eBMS eBMS API Methods](#ebms_api_methods)
3. [eBMS Endpoint URLs](#ebms_endpoint_url)

#### i. eBMS Settings
<a id="ebms_setting"></a>
![ebms_settings](https://github.com/navariltd/burundi_compliance/assets/60258622/fe0535f3-6b79-4d46-9ae7-f206513a28ea)

##### Details Tab
The first interface has fields for *username, password, and company*.
- Fill in the username and password provided by [OBR](https://obr.bi/index.php/systeme-de-facturation-electronique-ebms) upon application.
- The company field will be automatically filled if you have a single company. Otherwise, select the corresponding company.
- By default, the details are for production. For testing, tick the **sandbox** option.

##### Tax Tab
This tab contains details related to your organization's taxes.

##### More Info Tab
This tab has two fields:
1. Maximum Attempts: Enter the number of retries you want the system to attempt when the OBR server is down.
2. Retry Delay: This is the interval between retries. Enter the duration in seconds.

If multi-companies within one site, make settings for each company, since username and password will be diferent. But only one company per doctype.

#### <a id="ebms_api_methods"></a> ii. eBMS API Methods
![Screenshot from 2024-03-23 10-09-10](https://github.com/navariltd/burundi_compliance/assets/60258622/3bbda9f8-0273-4a74-a51f-37d8d429a274)

This comes with predefined 6 api methods, Incase of new method you can add it as new ebms api method.
This helps in our next doctype

#### iii. eBMS Endpoint URLs
<a id="ebms_endpoint_url"><a/>
![ebms_endpoint_urls](https://github.com/navariltd/burundi_compliance/assets/60258622/7707dffd-bb0d-4038-9b6b-9e0abc8ca95a)

1. **Create Sandbox and related Endpoint URL**:
   - Choose the environment as sandbox.
   - Enter the correct server URL provided by [OBR](https://obr.bi/index.php/systeme-de-facturation-electronique-ebms).
   - In the APIs child table, select methods and enter the corresponding endpoint URL ending with a slash (/). **Save**.

2. **Create Production with related Endpoint URL**:
   - Once you have the production endpoints and server URL, create the production environment with corresponding URLs.

This doctype will only have two transactions: sandbox and production.


## 2. Stock Movement
![stock_entry](https://github.com/navariltd/burundi_compliance/assets/60258622/1a69c858-93a5-4f62-a3bb-92241681daa8)

- **E-Tracker** Checkbox and **Re-Submit** Button:
  - After saving a document involving stock movements, an **E-Tracker** checkbox and a **Re-Submit** button appear.
  - Upon submission, a confirmation pop-up  appears:
  >"**Stock movement sent to OBR**" 
  - On reload, the **E-Tracker** checkbox is automatically ticked.
  
- **Stock Ledger Entry**:
  ![stock_ledger_entry](https://github.com/navariltd/burundi_compliance/assets/60258622/05410074-15c6-4dfa-96e4-b27cef6f9c66)

  - Similarly, related **Stock Ledger Entries** have an **E-Tracker** checkbox.
  - While the request is pending, the **E-Tracker** checkbox is unticked, and the **Re-submit** button appears.
  - If the maximum attempts are exhausted, an email notifies the unsuccessful request. Resend by clicking the **Re-submit** button.

- **Handling Many Unsent Transactions**:
  - If the OBR server is down, two options are available:
    1. A scheduler runs every 6 hours to send pending stock ledger entries automatically.
    2. For transactions like Stock Entry or Stock Reconciliation:
       - Filter transactions with **E-Tracker** equals "No".
       - Select pending entries, click the Action group button, and choose **eBIMS Tracker** to send to OBR.
  - It's recommended to rely on the scheduler for handling unsent transactions.
  ![schedular_job](https://github.com/navariltd/burundi_compliance/assets/60258622/a574f86c-f363-4e03-b4ee-0322b701bf97)

 
 ## 3. Selling
This is where OBR want to track all the company revenues.
### Doctypes
i.[Customer](#customer)
ii.[Delivery Note](#delivery_note)
ii.[Sales Invoice](#sales_invoice)
iii.[POS Invoice](#pos_invoice)


#### i. Customer
![Customer](https://github.com/navariltd/burundi_compliance/assets/60258622/ddb85831-6aed-4e4b-9538-c0254c63e355)

On the Tax Tab:
- Select the appropriate *GST Category* (e.g., select "Registered" if the customer is registered).
- Enter the Tax ID/TIN.
- Upon saving, the Tax ID is sent to OBR for registration confirmation.
  - Confirmation message received:
    > "NIF du contribuable connu."
- The "TIN Verified" checkbox is ticked upon successful verification.
- If the customer is unregistered (selected Unregistered from GST category), simply save without confirmation.


#### ii. Sales Invoice
![payments](https://github.com/navariltd/burundi_compliance/assets/60258622/060f8f63-2589-4847-9c84-9823b22e2174)

To send your invoice to OBR, follow these steps:
- Select *Customer* and *Items*.
- Choose the *Payment Type* from additional normal fields.
- If the customer is exempted from tax, ensure to tick the corresponding checkbox.
- Select the tax template *Sales Taxes and Charges Template* if tax is involved.
- Save and submit your document.

Upon submission, a pop-up message will appear:
> "Invoice sent to OBR"

Check the eBMS Tab:
![Screenshot from 2024-03-23 12-16-01](https://github.com/navariltd/burundi_compliance/assets/60258622/6a8f216e-ee8f-45c1-9095-2fef42d83701)

- The Read Only tab will display the response from OBR, including:
  - *Invoice Registered No.*
  - *Invoice Registered Date*
  - *Invoice Identifier*
  - *eBMS Signature*
- The checkbox *eBMS Submission* will be ticked.

Print the sales invoice; it will contain the Invoice Identifier (created even when the invoice is yet to reach the OBR).



**Credit Note:**
- To send a credit note:
  1. Click on **Create** at the top of the respective sales invoice.
  2. Choose **Return/Credit Note**.
  3. Enter the reason for creating the credit note (on the eBMS tab).
  4. Save and *Submit*.

**Reimbursement Deposit (RC):**
- To create a reimbursement deposit (RC):
  1. Create a credit note.
  2. Enter the reason.
  3. Tick the **Creating Payment Entry**.
  4. Save and *Submit*.

**Cancel Sales Invoice:**
- To cancel a sales invoice:
  1. Enter the reason for cancellation (found in the eBMS Tab).
  2. Save and *Cancel*.
     - Response received:
       > "Invoice cancelled successfully! La facture avec la signature (invoice identifier) a été annulée avec succès!"



#### Handling Pending Batch

When the OBR server is down, the system retries sending requests through a background job while users continue with normal processes. 

If the maximum retry attempts are reached, the sales invoice initiator receives an email notification of failure (indicating failure to reach the server). In such cases, contacting OBR for feedback is recommended.

Once the issue is resolved, there are two approaches to send batches:
1. A scheduler runs every 6 hours, automatically sending the requests.
2. Manually, by navigating to the sales invoice list, filtering for **eBMS Submission** equals "No", selecting the relevant entries, and clicking "Submit to EBMS" from the Action menu.
![bulk_sales_invoices](https://github.com/navariltd/burundi_compliance/assets/60258622/153f5276-0b97-4ac3-a81e-89d9914d91c8)


## Addition
### Doctypes
1. **Company**
   - Check if your company is registered:
     - Save your details in the Company doctype, including Tax ID.
     - Click the **Confirm TIN** button.
     - If your TIN is valid, it will display the company name.

2. **Supplier**
   - Upon saving a supplier:
     - The system checks if the supplier is registered.
     - If registered, the **TIN Verified** checkbox is automatically ticked.


## FAQS 


### <center>License</center>

  

<center>GNU General Public License (v3). See [license.txt](https://github.com/navariltd/burundi_compliance/blob/master/license.txt) for more information.</center>
