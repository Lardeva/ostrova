 INSERT INTO "OSTROVA"."SALOON"   SELECT   "ID", 	"NAME", 	"CLUB_ID" FROM   OSTROVA_IMP.SALON;
 INSERT INTO "OSTROVA"."CLUB"     "CLUB_ID", 	"NAME", 	"ZALA_PRICE", 	"ADDRESS"   FROM     OSTROVA_IMP.CLUB;
  INSERT INTO "OSTROVA"."SUPPLIER"   SELECT   	"SUP_ID", 	"NAME", 	"DESCRIPTION" FROM   OSTROVA_IMP."SUPPLIER";

 INSERT INTO OSTROVA.auth_user
  SELECT
  OSTROVA.AUTH_USER_SQ.NEXTVAL,
  'pbkdf2_sha256$30000$9aXR09FpiobP$agauh1MJYeL407Z+4rqXUPrX8erGQTRbsTPgD7T2los=',
  null,
  1,
  username,
  name,
  grupa,
  null,
  1,
  1,
  sysdate
FROM
  OSTROVA_IMP."STAFF";


insert into ostrova.article_group
select
  ostrova.article_group_sq.nextval,
  STOKA_GROUP,
  sysdate,
   1,
   0
  from (
  select STOKA_GROUP
  from ostrova_imp.stoka
group by STOKA_GROUP);

insert into ostrova.article
select
  stoka_id,
  descr,
  null,
  price,
  null,
  laST_PRICE,
  null,
  LAST_UPDATE_DATE,
 nvl((select ID from OSTROVA.ARTICLE_GROUP z where z.NAME = X.STOKA_GROUP),0) GROUP_ID
 from ostrova_imp.stoka x
;

-- fix sequence

drop sequence OSTROVA.ARTICLE_SQ;

declare
 v_sql varchar2(1000);
begin
SELECT 'CREATE SEQUENCE OSTROVA.ARTICLE_SQ MINVALUE 0 START WITH '||to_char(MAX(id)+1)||' INCREMENT BY 1 '
  INTO v_sql  FROM OSTROVA.ARTICLE;
EXECUTE IMMEDIATE v_sql;
end;
/


delete from OSTROVA_IMP.RECORD_ORDERS where order_id in (1,2);

INSERT INTO OSTROVA.DELIVERY
SELECT
ORDER_ID x,
ORDER_DATE,
STATUS,
DOSTAVKA_DATE,
FAKT_NO,
FIRM_FAKT_NO,
PLATENO,
NOTES,
ORDER_AMOUNT,
sysdate,
(select ID from OSTROVA.CLUB z where z.NAME = X.CLUB_NAME) CLUB_ID,
nvl((select ID from OSTROVA.AUTH_USER z where z.FIRST_NAME = X.SLUJITEL),1) user_ID,
kasa_no,
nvl((select nvl(ID,0) from OSTROVA.SUPPLIER z where z.NAME = X.FIRM),0) SUP_ID
FROM OSTROVA_IMP.RECORD_ORDERS X;

INSERT INTO OSTROVA.DELIVERY_DETAIL
SELECT
ostrova.delivery_detail_sq.nextval,
cnt,
price,
PRICE_ACTUAL,
ARTICE_ID,
STOKA_ID,
ORDER_ID,
nvl((select ID from OSTROVA.ARTICLE_GROUP z where z.NAME = X.GROUP_NAME),0) GROUP_ID
FROM OSTROVA_IMP.RECORD_ORDERS_DETAIL X;


INSERT INTO OSTROVA.ARTICLE_GROUP
  SELECT
    ostrova.article_group_sq.nextval,
    NAME,
    LAST_UPDATE_DATE,
    0,
    1
  FROM
    OSTROVA_IMP.GROUPS;


insert into OSTROVA.article_group values(0, 'MISSING', sysdate, 0,1);

insert into OSTROVA.article_group values(1, 'DELETED', sysdate, 0,1);

alter Table ostrova.article add old_id number;

INSERT INTO OSTROVA.ARTICLE
	  SELECT
		OSTROVA.ARTICLE_SQ.nextval,
		NAME,
		null,
		null,
		PRICE,
		null,
		PRICE,
		LAST_UPDATE_DATE,
		(select ID from ostrova.article_group where name = nvl((select name from OSTROVA_IMP.GROUPS z where z.ID = X.GROUP_ID),'MISSING') and order_type = 1) grupa,
		MIARKA,
		1,
		ID
	FROM
	  OSTROVA_IMP."ARTIKUL_TYPES" x;

update OSTROVA.ARTICLE set active = 0 where group_fk_id = 0;

-- insert missing old articles from old orders (hm, needed to be executed 3 times)
-- aggressive search of old and deleted articles, which do not have a record any more in original article (artikul_types) table. These are loaded in a special group (id 1 - "deleted")
-- articles are taken direclty from record_article, since they are only located there.
-- this is necessary, not to break master/detail relationship in order/ordeR_detail records.
-- the articles are inserted as inactive
INSERT INTO OSTROVA.ARTICLE
select
    OSTROVA.ARTICLE_SQ.nextval,
    NAME,
    NULL,
    NULL,
    PRICE,
    NULL,
    sysdate,
    0,
    null,
    0,
    ARTICLE_TYPE_ID
from "OSTROVA_IMP"."RECORD_ARTICLE"
where ARTICLE_TYPE_ID in (
     select max(ARTICLE_TYPE_ID) from "OSTROVA_IMP"."RECORD_ARTICLE" group by NAME where ARTICLE_TYPE_ID not in (select old_id from ostrova.article)
);

INSERT INTO OSTROVA.ARTICLE
select
    OSTROVA.ARTICLE_SQ.nextval,
    NAME,
    NULL,
    NULL,
    0,
    NULL,
    NULL,
    sysdate,
    1,
    null,
    0,
    ARTICLE_TYPE_ID
from (
select
    NAME,
    ARTICLE_TYPE_ID
from "OSTROVA_IMP"."RECORD_ARTICLE"
where ARTICLE_TYPE_ID in (
     select max(ARTICLE_TYPE_ID) from "OSTROVA_IMP"."RECORD_ARTICLE" where ARTICLE_TYPE_ID not in (select old_id from ostrova.article where old_id is not null)  group by NAME
) group by name, article_type_id
)
;

INSERT INTO OSTROVA.ARTICLE
select
    OSTROVA.ARTICLE_SQ.nextval,
    NAME,
    NULL,
    NULL,
    0,
    NULL,
    NULL,
    sysdate,
    1,
    null,
    0,
    ARTICLE_TYPE_ID
from (
select
    NAME,
    ARTICLE_TYPE_ID
from "OSTROVA_IMP"."RECORD_ARTICLE"
where ARTICLE_TYPE_ID in (
     select max(ARTICLE_TYPE_ID) from "OSTROVA_IMP"."RECORD_ARTICLE" where ARTICLE_TYPE_ID not in (select old_id from ostrova.article where old_id is not null)  group by NAME
) group by name, article_type_id
)
;

INSERT INTO OSTROVA."ORDER"
	  SELECT
		REC_ID,
		REC_DATE,
		REC_TIME_SLOT,
		REC_TIME,
		REC_TIME_END,
		PHONE,
		PARENT,
		CHILD,
		AGE,
		CHILD_COUNT,
		ADULT_COUNT,
		ZALA_COUNT,
		ZALA_PRICE,
		KAPARO,
		DISCOUNT,
		PRICE_FINAL,
		KAPARO_DATE,
		PAYMENT_DATE,
		VALIDITY_DATE,
		OTKAZ_DATE,
		OTKAZ_REASON,
		ZAIAVKA_DATE,
		NOTES,
		ADDRESS,
		EMAIL,
		CREATE_DATE,
		LAST_UPDATE_DATE,
		KAPARO2,
		KAPARO2_DATE,
		UPDATE_STATE,
		LOCKED,
		PAYED_FINAL,
		NOTES_TORTA,
		NOTES_KITCHEN,
		nvl((select ID from OSTROVA.saloon z where z.NAME = X.ADULT_SALOON and z.club_fk_id = x.club_id), 14 ) xx,
		nvl((select ID from OSTROVA.AUTH_USER z where z.FIRST_NAME = X.priel_porachka),1) user_ID,
		CLUB_ID,
		CHANGES
		FROM
	  OSTROVA_IMP.Record_data x where rec_id > 57;

-- aggressive search of old and deleted articles, which do not have a record any more in original article (artikul_types) table. These are loaded in a special group (id 1 - "deleted")
-- this is necessary, not to break master/detail relationship in order/ordeR_detail records.
INSERT INTO OSTROVA.ORDER_DETAIL
	select
	OSTROVA.OSTROVACALENDAR_ORDERDETAIL_SQ.NEXTVAL,
    CNT,
	PRICE,
    (select ID from ostrova.article z where (z.old_id = x.ARTICLE_TYPE_ID and z.name = x.NAME and z.group_fk_id = 1) or (z.old_id = x.ARTICLE_TYPE_ID and z.group_fk_id <> 1) ) article_id,
	(select GROUP_FK_ID from ostrova.article z where (z.old_id = x.ARTICLE_TYPE_ID and z.name = x.NAME and z.group_fk_id = 1) or (z.old_id = x.ARTICLE_TYPE_ID and z.group_fk_id <> 1)) article_id,
    REC_ID
	from
 "OSTROVA_IMP"."RECORD_ARTICLE" x
 where rec_id in (select id from OSTROVA."ORDER");

-- fix total exceptions with missing article names
INSERT INTO OSTROVA.ARTICLE
values(
    OSTROVA.ARTICLE_SQ.nextval,
    'Детско меню',
    NULL,
    NULL,
    0,
    NULL,
    NULL,
    sysdate,
    1,
    null,
    0,
    9998);

update OSTROVA.ORDER_DETAIL set article_fk_id = (select max(id) from OSTROVA.ARTICLE) , group_fk_id = 1 where article_fk_id is null and order_fk_id in (6148,6205,7815,7856);


 -- original non-aggressive artcile search
/*INSERT INTO OSTROVA.ORDER_DETAIL
	select
	OSTROVA.OSTROVACALENDAR_ORDERDETAIL_SQ.NEXTVAL,
    CNT,
	PRICE,
    (select ID from ostrova.article z where z.old_id = ARTICLE_TYPE_ID) article_id,
	(select GROUP_FK_ID from ostrova.article z where z.old_id = ARTICLE_TYPE_ID) article_id,
    REC_ID
	from
 "OSTROVA_IMP"."RECORD_ARTICLE"
 where rec_id in (select id from OSTROVA."ORDER");
*/

INSERT INTO OSTROVA.ARTICLE


	  SELECT
		OSTROVA.ARTICLE_SQ.nextval,
		NAME,
		null,
		null,
		PRICE,
		null,
		PRICE,
		LAST_UPDATE_DATE,
		(select ID from ostrova.article_group where name = nvl((select name from OSTROVA_IMP.GROUPS z where z.ID = X.GROUP_ID),'MISSING') and order_type = 1) grupa,
		MIARKA,
		1,
		ID
	FROM
	  OSTROVA_IMP."ARTIKUL_TYPES" x;


alter Table ostrova.article drop column old_id;

drop sequence "OSTROVA"."SUPPLIER_SQ";
CREATE SEQUENCE  "OSTROVA"."SUPPLIER_SQ"  MINVALUE 1 MAXVALUE 9999999999999999999999999999 INCREMENT BY 1 START WITH 1000 CACHE 20 NOORDER  NOCYCLE ;

commit;





