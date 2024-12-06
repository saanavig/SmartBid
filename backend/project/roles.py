#declare different roles here to be called later

#user types
USER = 'U'
SUPERUSER = 'S'
VISITOR = 'V'
VIP = 'VIP'
user_types = [
    (USER,'User'),
    (SUPERUSER, 'Superuser'),
    (VISITOR, 'Vistor'),
    (VIP, 'VIP')]

#availability
SOLD = 'S'
RENTED = 'R'
FOR_SALE = 'FS'
FOR_RENT = 'FR'
availability = [
    (SOLD, 'Sold'),
    (RENTED, 'Rented'),
    (FOR_SALE, 'For Sale'),
    (FOR_RENT, 'For Rent')]

#bid status
PENDING_BID = 'P'
ACCEPTED_BID = 'A'
REJECTED_BID = 'R'
bid_status = [
    (PENDING_BID, 'Pending'),
    (ACCEPTED_BID, 'Accepted'),
    (REJECTED_BID, 'Rejected')]

#transaction status
PENDING_TRANS = 'P'
COMPLETED_TRANS = 'C'
REJECTED_TRANS = 'R'
transaction_status = [
    (PENDING_TRANS, 'Pending'),
    (COMPLETED_TRANS, 'Completed'),
    (REJECTED_TRANS, 'Rejected')]

#complaints
PENDING_COMP = 'P'
RESOLVED_COMP = 'R'
complaint_status = [
    (PENDING_COMP, 'Pending'),
    (RESOLVED_COMP, 'Resolved')]

#user_applications
PENDING_APP = 'P'
APPROVED_APP = 'A'
REJECTED_APP = 'R'
user_application_status = [
    (PENDING_APP, 'Pending'),
    (APPROVED_APP, 'Approved'),
    (REJECTED_APP, 'Rejected')]

#vip status
PENDING_VIP = 'P'
ACTIVE_VIP = 'A'
EXPIRED_VIP = 'E'
vip_status = [
    (PENDING_VIP, 'Pending'),
    (ACTIVE_VIP, 'Active'),
    (EXPIRED_VIP, 'Expired')]