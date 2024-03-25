# <center>Burundi Compliance</center>

  

  

## <center> OBR Integration for ERPNext</center>

  

  

  

### Overview

  

The Burundi Compliance app seamlessly integrates OBR tax functionalities into ERPNext, empowering users to efficiently manage tax compliance tasks.

Developed on the robust Frappe Framework and ERPNext platform, it streamlines repetitive tasks and simplifies the tax compliance process for businesses.

  

### Installation

  

  

#### Manual/Self-Hosted Installation

  

  

1. [Install bench](https://github.com/frappe/bench)

  

2. [Install ERPNext](https://github.com/frappe/erpnext#installation)

  

  

3. Once bench and ERPNext are installed, add burundi_compliance to your bench by running:

  

  

```sh

  

  

$  bench  get-app  --branch  {branch-name}  https://github.com/navariltd/burundi_compliance.git

  

  

```

  

  

Replace `{branch-name}` with the desired branch name from the repository. Ensure compatibility with your installed versions of Frappe and ERPNext.

  

  

4. Install the burundi_compliance app on your site by running:

  

  

```sh

  

  

$  bench  --site  {sitename}  install-app  burundi_compliance

  

  

```

  

  

Replace `{sitename}` with the name of your site.

  

#### Frappe Cloud Installation

- Sign up with Frappe Cloud.

- Setup a [bench](https://frappecloud.com/docs/benches/create-new).

- Create a new site.

- Choose Frappe Version-14/Version-15 or above, and select ERPNext, Lending and Burundi Compliance from the available Apps to Install.

- Within minutes, the site should be up and running with a fresh install, ready to explore the app's simple and impressive features.

  

If assistance is needed to get started, reach out for consultation and support from [Navari](https://chat.openai.com/c/solutions@navari.co.ke).

  

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

4. [Item](#item)

  

  

#### i. eBMS Settings

  

<a  id="ebms_setting"></a>

  

![ebms_settings](https://github.com/navariltd/burundi_compliance/assets/60258622/fe0535f3-6b79-4d46-9ae7-f206513a28ea)

  

  

##### Details Tab

  

The first interface has fields for *username, password, and company*.

  

- Fill in the username and password provided by [OBR](https://obr.bi/index.php/systeme-de-facturation-electronique-ebms) upon application.

  

- The company field will be automatically filled if you have a single company. Otherwise, select the corresponding company.

  

- By default, the details are for production. For testing, tick the **sandbox** checkbox.

  

  

##### Tax Tab

  

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

  

This tab has two fields:

  

1. Maximum Attempts: Enter the number of retries you want the system to attempt when the OBR server is down.

  

2. Retry Delay: This is the interval between retries. Enter the duration in seconds.

  

  

If multi-companies within one site, make settings for each company, since username and password will be diferent. But only one company per doctype.

  

  

#### <a id="ebms_api_methods"></a> ii. eBMS API Methods

  

![Screenshot from 2024-03-23 10-09-10](https://github.com/navariltd/burundi_compliance/assets/60258622/3bbda9f8-0273-4a74-a51f-37d8d429a274)

  

  

This comes with predefined 6 api methods, Incase of new method you can add it as new ebms api method.

  

This helps in our next doctype

  

  

#### iii. eBMS Endpoint URLs

  

<a  id="ebms_endpoint_url"><a/>

  

![ebms_endpoint_urls](https://github.com/navariltd/burundi_compliance/assets/60258622/7707dffd-bb0d-4038-9b6b-9e0abc8ca95a)

  

  

1.  **Create Sandbox and related Endpoint URL**:

  

- Choose the environment as sandbox.

  

- Enter the correct server URL provided by [OBR](https://obr.bi/index.php/systeme-de-facturation-electronique-ebms).

  

- In the APIs child table, select methods and enter the corresponding endpoint URL ending with a slash (/). **Save**.

  

  

2.  **Create Production with related Endpoint URL**:

  

- Once you have the production endpoints and server URL, create the production environment with corresponding URLs.

  

  

This doctype will only have two transactions: sandbox and production.

  

#### <a id="item"></a> iv. Item

  

To ensure accurate tracking by OBR, it's essential to set up the system properly. If an item falls under the classification of goods that OBR monitors, it's important to enable this feature upon creation.

  

This configuration involves ticking the **Allow OBR to track...** checkbox, which can be found in three tabs:

  

-  **Inventory**: This option enables OBR to track stock movements for the item, recording any incoming or outgoing movements.

-  **Purchase**: Enabling this option allows OBR to track the item's movement during purchase transactions.

-  **Sales**: By default, this option is already ticked. It permits OBR to monitor any sales involving the item.

  

By activating these checkboxes, you ensure comprehensive tracking of relevant activities by OBR, enhancing overall monitoring and compliance.

  

  

## 2. Stock Movement

  

![stock_entry](https://github.com/navariltd/burundi_compliance/assets/60258622/1a69c858-93a5-4f62-a3bb-92241681daa8)

  

  

-  **E-Tracker** Checkbox and **Re-Submit** Button:

  

- After saving a document involving stock movements, an **E-Tracker** checkbox and a **Re-Submit** button appear.

  

- Upon submission, a confirmation pop-up appears:

  

>"**Stock movement sent to OBR**"

  

- On reload, the **E-Tracker** checkbox is automatically ticked.

  

-  **Stock Ledger Entry**:

  

![stock_ledger_entry](https://github.com/navariltd/burundi_compliance/assets/60258622/05410074-15c6-4dfa-96e4-b27cef6f9c66)

  

  

- Similarly, related **Stock Ledger Entries** have an **E-Tracker** checkbox.

  

- While the request is pending, the **E-Tracker** checkbox is unticked, and the **Re-submit** button appears.

  

- If the maximum attempts are exhausted, an email notifies(doc owner) about the unsuccessful request. Resend by clicking the **Re-submit** button.

  

**Purchase Receipt/Purchase Invoice**

When purchasing an item that needs to be tracked, the purchase receipt will automatically send data to OBR upon submission.

  

In cases where a user creates a purchase invoice directly without a purchase receipt, they should tick the *Update Stock* checkbox to enable tracking for the item.

  
  

-  **Handling Many Unsent Transactions**:

  

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

  

- [Customer](#customer)

  

- [Delivery Note](#delivery_note)

  

- [Sales Invoice](#sales_invoice)

  

- [POS Invoice](#pos_invoice)

  

  

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

  

#### ii. Delivery Note

Upon creation of a delivery note, upon submission, it updates the stock and sends a similar payload to OBR.

The document includes an E-Tracker checkbox, which is ticked upon receiving a response.

  

**Updating Stock with Sales Invoice**

If a company decides to bypass the delivery note, they can update stock directly in the sales invoice by ticking the *Update Stock* checkbox. Upon clicking submit, two requests will be sent to OBR: one to add stock movement and the other to add the invoice.

  
  

#### iii. Sales Invoice

  

![payments](https://github.com/navariltd/burundi_compliance/assets/60258622/060f8f63-2589-4847-9c84-9823b22e2174)

  

  

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

  

![Screenshot from 2024-03-23 12-16-01](https://github.com/navariltd/burundi_compliance/assets/60258622/6a8f216e-ee8f-45c1-9095-2fef42d83701)

  

  

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

  

![bulk_sales_invoices](https://github.com/navariltd/burundi_compliance/assets/60258622/153f5276-0b97-4ac3-a81e-89d9914d91c8)

  

### iv. POS Invoice

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

  

  

## FAQS
1. What happens when you tick update stock on POS Invoice, does it send two request to OBR?
>Yes, but they dont happen at the same time.
>First, te invoice will be sent to OBR. Then later when we close the entry for POS, it will create stock ledger entry for items sold, at this point, the schedular will send the stock details to OBR.

  

  

### <center>License</center>

  

  

  

<center>GNU General Public License (v3). See [license.txt](https://github.com/navariltd/burundi_compliance/blob/master/license.txt) for more information.</center>
