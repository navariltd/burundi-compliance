# <center>Burundi Compliance</center>

## <center> OBR Integration for ERPNext</center>

  
### Overview

The Burundi Compliance app seamlessly integrates OBR tax functionalities into ERPNext, empowering users to efficiently manage tax compliance tasks.

Developed on the robust Frappe Framework and ERPNext platform, it streamlines repetitive tasks and simplifies the tax compliance process for businesses.

### Summary of Key Features:

1. **Sales Invoice Tax Tracking:** 
   - Seamlessly send sales invoices to OBR for meticulous tax tracking, ensuring adherence to regulatory standards and facilitating transparent financial reporting.

2. **Stock Movement Monitoring:** 
   - Track stock movements for sales transactions within ERPNext, enabling comprehensive oversight and compliance with tax regulations governing inventory management.

3. **Supplier/Customer Registration Verification:** 
   - Automatically verify supplier/customer registration status, ensuring that only registered members are engaged in business transactions, thereby mitigating risks associated with non-compliant suppliers.

4. **Real-Time TIN Verification:** 
   - Verify Tax Identification Numbers (TINs) of registered customers in real-time, validating their authenticity and promoting compliance with tax regulations.

5. **Automated Compliance Checks:** 
   - Implement automated compliance checks to enforce adherence to tax regulations at every stage of business operations, reducing the risk of non-compliance and associated penalties.

### Architecture Overview
Streamlined Integration: ERPNext Communicating with OBR Server and Database
(#Image)

### Specifications
- English Version: [SPECIFICATIONS D'INTERFACAGE EBMS - Eng.docx](https://github.com/navariltd/burundi_compliance/files/14740821/SPECIFICATIONS.D.INTERFACAGE.EBMS.-.Eng.docx)
- French Version: [SPECIFICATIONS D'INTERFACAGE EBMS - ACCUSE RECEPTION.docx](https://github.com/navariltd/burundi-compliance/files/14821851/SPECIFICATIONS.D.INTERFACAGE.EBMS.-.ACCUSE.RECEPTION.docx)
#### Manual/Self-Hosted Installation

1. [Install bench](https://github.com/frappe/bench)

  

2. [Install ERPNext](https://github.com/frappe/erpnext#installation)

    

3. Once bench and ERPNext are installed, add burundi-compliance to your bench by running:

  
```sh


$  bench  get-app  --branch  {branch-name}  https://github.com/navariltd/burundi-compliance.git

```


Replace `{branch-name}` with the desired branch name from the repository. Ensure compatibility with your installed versions of Frappe and ERPNext.


4. Install the burundi-compliance app on your site by running:


```sh

$  bench  --site  {sitename}  install-app  burundi-compliance

```

Replace `{sitename}` with the name of your site.

  

#### Frappe Cloud Installation

- Sign up with Frappe Cloud.

- Setup a [bench](https://frappecloud.com/docs/benches/create-new).

- Create a new site.

- Choose Frappe Version-14/Version-15 or above, and select ERPNext, and Burundi Compliance from the available Apps to Install.

- Within minutes, the site should be up and running with a fresh install, ready to explore the app's simple and impressive features.

  

If assistance is needed to get started, reach out for consultation and support from: [Navari](https://navari.co.ke/).

  

### Troubleshooting

- If you encounter any errors during installation, refer to the error messages for guidance.

- Ensure all dependencies are correctly installed and compatible with the versions specified.

  

  

## Key Features

  

1.[Setup](#setup)

  

2.[Stock Movement](#Stock_Movement)

  

3.[Selling](#Selling)

  

  

### <a id="setup"></a> 1. Setup

  

I believe we can see a Burundi Compliance module when we log into the system.

  

It has a workspace with three shortcuts to various custom doctypes.

  

  

#### Doctypes

  

1. [eBMS Settings](#ebms_setting)

  

2. [eBMS eBMS API Methods](#ebms_api_methods)

  

3. [eBMS Endpoint URLs](#ebms_endpoint_url)

4. [Item](#item)

  

  

#### i. eBMS Settings

  

<a  id="ebms_setting"></a>

  

![re-re-Ebms](https://github.com/navariltd/burundi-compliance/assets/60258622/f36e3afc-2443-4a2c-a733-2a2bf81634aa)

  

  

##### Details Tab

  

The first interface has fields for *username, password, and company*.

- Fill in the username and password provided by [OBR](https://obr.bi/index.php/systeme-de-facturation-electronique-ebms) upon application.

- The company field will be automatically filled if you have a single company. Otherwise, select the corresponding company.

- By default, the details are for production. For testing, tick the **sandbox** checkbox.

  

  

##### Tax Tab

  ![Screenshot from 2024-03-25 10-19-16](https://github.com/navariltd/burundi-compliance/assets/60258622/11ce1aef-9130-42a7-a116-beeeba9252ca)


This tab contains details related to your organization's taxes. This are mendatory because they are mendatory when sending the Invoice.

-*Taxpayer's Sector of Activity* - this is the company domain

-*Taxpayer's Legal Form* -

-*The taxpayer's commercial register number*-This is the trade number of the company

-*Subject to VAT* -

-*System Identification*- taxpayer system number(computer serial no.)

-*Type of Taxpayer* -

-*Subject to Consumption Tax*

-*Subject to FlatRate Withholding Tax* -

  

##### More Info Tab

  
![Screenshot from 2024-04-01 12-02-00](https://github.com/navariltd/burundi-compliance/assets/60258622/a8399448-aa48-4422-80f1-d81036eed69a)

This tab has frequency schedular fields:

  

1. Maximum Attempts: Enter the number of retries you want the system to attempt when the OBR server is down.

  

2. Retry Delay: This is the interval between retries. Enter the duration in seconds.
3.  **Invoice Event Frequency**: This option controls how often the system automatically sends invoices to OBR. Choose the frequency that best matches how often you want your invoices sent. Consider factors like your sales volume and when you prefer to submit invoices to OBR.
    
4.  **Stock Movement Event Frequency**: This option sets how often the system sends stock movement data to OBR. Choose a frequency that aligns with your needs for updating OBR on stock changes.
    
5.  **Setting a Specific Time for Invoice Sending**: If you want to send invoices at a specific time each day, you can use a feature called Cron. When you select this option, another field will appear where you can enter a special format called Cron. You can use a website like [Crontab Guru](https://crontab.guru/) to help you get the timing right. For example, if you want to send invoices every day at 12:00 pm, you would enter "0 12 * * *" in the Cron format field.

6.  **Allow OBR to track sales**: This setting controls whether the system will send invoices to OBR for tracking purposes. When enabled, invoices will be automatically sent to OBR. When disabled, invoices will not be sent to OBR.
    
7.  **Allow OBR to track stock movement**: This setting controls whether the system will track stock movement data and send it to OBR. When enabled, stock movement information will be automatically sent to OBR. When disabled, stock movement will not be tracked or sent to OBR.

If multi-companies are within one site, make settings for each company, since username and password will be different. But only one company per doctype.

  

  

#### <a id="ebms_api_methods"></a> ii. eBMS API Methods

  

![re_ebms_methods](https://github.com/navariltd/burundi-compliance/assets/60258622/4a7c7a42-ada0-4125-ba04-04bc576cb5d5)

  

  

This comes with predefined 6 api methods, Incase of new method you can add it as new ebms api method.

  

This helps in our next doctype

  

  

#### iii. eBMS Endpoint URLs

  

<a  id="ebms_endpoint_url"><a/>
![re_sbms_endpoint_urls](https://github.com/navariltd/burundi-compliance/assets/60258622/05ff00c3-762c-495b-9167-fb126e7dd650)
 

1.  **Create Sandbox and related Endpoint URL**:

  

- Choose the environment as sandbox.

  

- Enter the correct server URL provided by [OBR](https://obr.bi/index.php/systeme-de-facturation-electronique-ebms).

  

- In the APIs child table, select methods and enter the corresponding endpoint URL ending with a slash (/). **Save**.

  

  

2.  **Create Production with related Endpoint URL**:

  

- Once you have the production endpoints and server URL, create the production environment with corresponding URLs.

  

  

This doctype will only have two transactions: sandbox and production.

  

#### <a id="item"></a> iv. Item

  ![re_item_tests](https://github.com/navariltd/burundi-compliance/assets/60258622/5ae687d7-8b10-4999-b052-5debb4a371d7)


To ensure accurate tracking by OBR, it's essential to set up the system properly. If an item falls under the classification of goods that OBR monitors, it's important to enable this feature upon creation.

  

This configuration involves ticking the **Allow OBR to track...** checkbox, which can be found in three tabs:

  

-  **Inventory**: This option enables OBR to track stock movements for the item, recording any incoming or outgoing movements.

-  **Purchase**: Enabling this option allows OBR to track the item's movement during purchase transactions.

-  **Sales**: By default, this option is already ticked. It permits OBR to monitor any sales involving the item.

  

By activating these checkboxes, you ensure comprehensive tracking of relevant activities by OBR, enhancing overall monitoring and compliance.

  

  

## 2. <a id="Stock_Movement"></a>Stock Movement

  

![re_test_stock_entry](https://github.com/navariltd/burundi-compliance/assets/60258622/bb6794b5-ef84-45b6-9fbb-af99b4788f50)

  

  

-  **E-Tracker** Checkbox and **Re-Submit** Button:

  

- After saving a document involving stock movements, an **E-Tracker** checkbox and a **Re-Submit** button appear.

  

- Upon submission, a confirmation pop-up appears:

  

>"**Stock movement sent to OBR**"

  

- On reload, the **E-Tracker** checkbox is automatically ticked.

  

-  **Stock Ledger Entry**:

  

![re_stock_ledger](https://github.com/navariltd/burundi-compliance/assets/60258622/5df74623-34d0-4861-add7-f8cdf3040ef6)

  

  

- Similarly, related **Stock Ledger Entries** have an **E-Tracker** checkbox.

  

- While the request is pending, the **E-Tracker** checkbox is unticked, and the **Re-submit** button appears.

  

- If the maximum attempts are exhausted, an email notifies(doc owner) about the unsuccessful request. Resend by clicking the **Re-submit** button.

  

**Purchase Receipt/Purchase Invoice**
![re_test_purchase_invoice](https://github.com/navariltd/burundi-compliance/assets/60258622/84e30890-bdb6-4385-b0ba-a2807c89d058)

When purchasing an item that needs to be tracked, the purchase receipt will automatically send data to OBR upon submission.

  

In cases where a user creates a purchase invoice directly without a purchase receipt, they should tick the *Update Stock* checkbox to enable tracking for the item.

  
  

-  **Handling Many Unsent Transactions**:

  

- If the OBR server is down, two options are available:

  

1. A scheduler runs every 6 hours to send pending stock ledger entries automatically.

  

2. For transactions like Stock Entry or Stock Reconciliation:

  

- Filter transactions with **E-Tracker** equals "No".

  

- Select pending entries, click the Action group button, and choose **eBIMS Tracker** to send to OBR.

  

- It's recommended to rely on the scheduler for handling unsent transactions.

  

![re_schedular_job](https://github.com/navariltd/burundi-compliance/assets/60258622/cd70665c-6a5f-4c51-b13d-a70caa23a613)

  

  

## 3. <a id="Selling"></a>Selling

  

This is where OBR want to track all the company revenues.

  

### Doctypes

  

- [Customer](#customer)

  

- [Delivery Note](#delivery_note)

  

- [Sales Invoice](#sales_invoice)

  

- [POS Invoice](#pos_invoice)

  

  

#### i. Customer

  

![re_customer](https://github.com/navariltd/burundi-compliance/assets/60258622/0a281ca9-f2f4-45a5-9738-16a58d1397b1)

  

  

On the Tax Tab:

  

- Select the appropriate *GST Category* (e.g., select "Registered" if the customer is registered).

  

- Enter the Tax ID/TIN.

  

- Upon saving, the Tax ID is sent to OBR for registration confirmation.

  

- Confirmation message received:

  

> "NIF du contribuable connu."

  

- The "TIN Verified" checkbox is ticked upon successful verification.

  

- If the customer is unregistered (selected Unregistered from GST category), simply save without confirmation.

  

#### ii. Delivery Note
![Screenshot from 2024-03-25 08-08-31](https://github.com/navariltd/burundi-compliance/assets/60258622/21b000c4-99ee-4628-8b35-d938a4e8887f)

Upon creation of a delivery note, upon submission, it updates the stock and sends a similar payload to OBR.

The document includes an E-Tracker checkbox, which is ticked upon receiving a response.

  

**Updating Stock with Sales Invoice**

If a company decides to bypass the delivery note, they can update stock directly in the sales invoice by ticking the *Update Stock* checkbox. Upon clicking submit, two requests will be sent to OBR: one to add stock movement and the other to add the invoice.

  
  

#### iii. Sales Invoice

  

![re_test_sales_invoice](https://github.com/navariltd/burundi-compliance/assets/60258622/5a0f69f0-26f4-48c8-addc-7499781f5647)

  

  

To send your invoice to OBR, follow these steps:

  

- Select *Customer*

- Add the *Items* to be sold.

- Choose the *Payment Type* from additional normal fields.

  

- If the customer is exempted from tax, ensure to tick the corresponding checkbox.

  

- Select the tax template *Sales Taxes and Charges Template* if tax is involved.

  

- Save and submit your document.

  

  

Upon submission, a pop-up message will appear:

  

> "Invoice sent to OBR"

  

  

Check the eBMS Tab:

  

![re_sales_invoice_ebms](https://github.com/navariltd/burundi-compliance/assets/60258622/6ce237c6-d142-4ba4-ac35-e3ba5539f434)

  

  

- The Read Only tab will display the response from OBR, including:

  

-  *Invoice Registered No.*

  

-  *Invoice Registered Date*

  

-  *Invoice Identifier*

  

-  *eBMS Signature*

  

- The checkbox *eBMS Submission* will be ticked.

  

  

Print the sales invoice; it will contain the Invoice Identifier (created even when the invoice is yet to reach the OBR).

(Sales Invoice print image)

  
  

  

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

  

**Differ Submission to OBR**

In case the user doesn't want to send the sales invoice to OBR at the time of submission, simply tick the *Differ Submission to OBR* checkbox (circled in the sales invoice image).

Later, one can untick the checkbox and use the *Re-submit* button to send the invoice to OBR.

  
  

#### Handling Pending Batch

  

  

When the OBR server is down, the system retries sending requests through a background job while users continue with normal processes.

  

  

If the maximum retry attempts are reached, the sales invoice initiator receives an email notification of failure (indicating failure to reach the server). In such cases, contacting OBR for feedback is recommended.

  

  

Once the issue is resolved, there are two approaches to send batches:

  

1. A scheduler runs every 6 hours, automatically sending the requests.

  

2. Manually, by navigating to the sales invoice list, filtering for **eBMS Submission** equals "No", selecting the relevant entries, and clicking "Submit to EBMS" from the Action menu.

  

(Add image of pending batch)
  

### iv. POS Invoice
![re_test_pos_invoice](https://github.com/navariltd/burundi-compliance/assets/60258622/c5edf8ae-b313-4d42-b7d0-32680c6d973a)

Similar to sales invoice, sends the data to OBR on **submit**.

The doctype has a section(eBMS) which stores response from the OBR.

It has similar fields like *Differ submission, payment type* etc.

  

## Addition

  

### Doctypes

  

1.  **Company**

  

- Check if your company is registered:

  

- Save your details in the Company doctype, including Tax ID.

  

- Click the **Confirm TIN** button.

  

- If your TIN is valid, it will display the company name.

  

  

2.  **Supplier**

  

- Upon saving a supplier:

  

- The system checks if the supplier is registered.

  

- If registered, the **TIN Verified** checkbox is automatically ticked.
  
3. **Address**
   ![Screenshot from 2024-04-01 11-45-07](https://github.com/navariltd/burundi-compliance/assets/60258622/03d4e46d-e297-4e13-b378-856daa22286a)

  This contains the location information required when sending invoices. Remember to fill all fields with *.
  - Rue
  - Avenue
  - Numero
  - Commune
  - Quartier
  - Town
  - Province
  
4.  **Integration Request**
When there's a need to check the status or details of an action like sending an invoice or recording stock movement, all the relevant information is available in this document type. If an invoice or stock movement fails to go through, the status will be marked as "Failed". If the action is successful, the status will be marked as "Completed". Additionally, this document records details about the payload, output and any errors encountered during the process.
    
5.  **Error Log**:
In the event of an action failing and needing more detailed information than what's provided in the Integration Request, the Error Log document comes into play. It contains comprehensive error logs with additional details, assisting in pinpointing exactly where the error occurred and providing more clarity on what went wrong.

## Summary of Endpoints

|                | ERPNext                                | OBR Server                                    |
|----------------|----------------------------------------|-----------------------------------------------|
| Authenticate User | Send user credentials                   | Receive request for authentication, verify credentials, issue access token             |
|                  | *Endpoint: `(/login`)*                  |                                               |
| Add Sales Invoice / POS Invoice | Send invoice details            | Receive request to add invoice, process the request, send confirmation                  |
|                                 | *Endpoint: `(/addInvoice_confirm/`)* |                                           |
| Add Stock Movements            | Send stock movement details       | Receive request to add stock movements, process the request, send confirmation         |
|                                 | *Endpoint: `(/AddStockMovement/`)* |                                          |
| Check TIN (Customer, Supplier) | Send TIN for verification         | Receive request to verify TIN, check TIN validity, return owner's name                 |
|                                 | *Endpoint: `(/checkTIN/`)*        |                                               |
| Cancel Sales Invoice           | Send invoice ID for cancellation  | Receive request to cancel invoice, process the request, send confirmation              |
|                                 | *Endpoint: `(/cancelInvoice/`)*   |                                               |
  

## FAQS
1. What happens when you tick update stock on POS Invoice, does it send two request to OBR?
>Yes, but they dont happen at the same time.
>First, te invoice will be sent to OBR. Then later when we close the entry for POS, it will create stock ledger entry for items sold, at this point, the schedular will send the stock details to OBR.

  

  

### <center>License</center>

  

  

  

<center>GNU General Public License (v3). See [license.txt](https://github.com/navariltd/burundi-compliance/blob/master/license.txt) for more information.</center>
