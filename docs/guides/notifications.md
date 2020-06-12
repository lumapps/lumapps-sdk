Notifications are well describe on the [official documentation](https://api.lumapps.com/docs/pages/notification)

---

Additional use case: **Send notification to a group of users** :

You need to retrieve the target group id, put it in the `feedKeys` list and remove the `recipientEmail` properties.

```json
notification_body = {
  "feedKeys": ["4589840722165660"], 
  "customerId": "123456789",
  "instanceId": "12345678",
  "type": "custom",
  "customType": "custom type identifier",
  "functionalInnerId": "external-reference",
  "senderEmail": "an admin.account@domain.com",
  "link": {"fr": "https://myexternalapplicationurl"},
  "title": {"en": "Notification title"},
  "description": {"en": "Notification content"},
  "group": true,
  "groupName": {"en": "Group name"},
  "groupDescription": {"en": "Group description"},
  "isReadOnClick": true,
  "notifyAuthor": false,
}
```