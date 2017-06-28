
-- ############## Импортиране на основни номенклатури
INSERT INTO "OSTROVA"."CLUB"     "CLUB_ID", 	"NAME", 	"ZALA_PRICE", 	"ADDRESS"   FROM     OSTROVA_IMP.CLUB;
INSERT INTO "OSTROVA"."SALOON"   SELECT   "ID", 	"NAME", 	"CLUB_ID", '1' FROM   OSTROVA_IMP.SALON;
INSERT INTO "OSTROVA"."SUPPLIER"   SELECT   	"SUP_ID", 	"NAME", 	"DESCRIPTION" FROM   OSTROVA_IMP."SUPPLIER";

-- Поправка на sequence, така че при добавяне на нови записи да не се получи конфликт с прехвърлените от старата
-- система идентификатори
drop sequence "OSTROVA"."CLUB_SQ";
CREATE SEQUENCE  "OSTROVA"."CLUB_SQ"  START WITH 1000;

drop sequence "OSTROVA"."SALOON_SQ";
CREATE SEQUENCE  "OSTROVA"."SALOON_SQ"  START WITH 1000;

drop sequence "OSTROVA"."SUPPLIER_SQ";
CREATE SEQUENCE  "OSTROVA"."SUPPLIER_SQ"  START WITH 1000;


 -- ############## Импортиране на съществуващите потребителски профили,
 -- парола по подразбиране 12345678
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

-- ############## Импортиране на артикули - доставка
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

-- Ръчна Поправка на sequence за артикули,
-- тъй като ще използваме оригиналните ID-та от старата база, за да се избегне нуждата от прегрупиране
drop sequence OSTROVA.ARTICLE_SQ;

declare
 v_sql varchar2(1000);
begin
SELECT 'CREATE SEQUENCE OSTROVA.ARTICLE_SQ MINVALUE 0 START WITH '||to_char(MAX(id)+1)||' INCREMENT BY 1 '
  INTO v_sql  FROM OSTROVA.ARTICLE;
EXECUTE IMMEDIATE v_sql;
end;
/

-- Първите два записа в оригиналната база са тестови и са непълни, затова се премахват
delete from OSTROVA_IMP.RECORD_ORDERS where order_id in (1,2);

-- ############## Импортиране на доставки
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

-- ############## Импортиране на доставки - детайни записи
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


-- ############## Импортиране на артикулни - поръчка
INSERT INTO OSTROVA.ARTICLE_GROUP
  SELECT
    ostrova.article_group_sq.nextval,
    NAME,
    LAST_UPDATE_DATE,
    0,
    1
  FROM
    OSTROVA_IMP.GROUPS;

-- добавяне на служебна група - артикули с липсваща група (съществувала и изтрита)
insert into OSTROVA.article_group values(0, 'MISSING', sysdate, 0,1);

-- добавяне на служебна група - липсващи артикули (изтрити)
insert into OSTROVA.article_group values(1, 'DELETED', sysdate, 0,1);

-- добавяне на "паразитна колона"
alter Table ostrova.article add old_id number;

-- ############## Импортиране на артикули - поръчка
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
		(select
		    ID
   	     from
   	        ostrova.article_group
         where
            name = nvl((select name from OSTROVA_IMP.GROUPS z where z.ID = X.GROUP_ID),'MISSING') and
            order_type = 1) grupa,
		MIARKA,
		1,
		ID
	FROM
	  OSTROVA_IMP."ARTIKUL_TYPES" x;

-- Артикулите с липсваща група се правят неактивни
update OSTROVA.ARTICLE set active = 0 where group_fk_id = 0;

-- Добавяне на лиспващите стари артикули от старите поръчки (изпълнява се на 3 паса за да се обхванат всички случаи)
-- Всички такива артикули се добавят към група DELETED (id=1)
-- Артикулите се добавят само с името си, тъй като присъстват единствено в старата таблица за поръчки
-- Това е необходимо за да не се наруши master/detail отношението в таблица order/detail
-- Всички артикули се добавят като неактивни (is_active=0)
INSERT INTO OSTROVA.ARTICLE
select
    OSTROVA.ARTICLE_SQ.nextval,
    NAME,
    NULL,
    NULL,
    PRICE,
    NULL,
    PRICE,
    sysdate,
    0,
    null,
    0,
    ARTICLE_TYPE_ID
from "OSTROVA_IMP"."RECORD_ARTICLE"
where ARTICLE_TYPE_ID in (
     select
        max(ARTICLE_TYPE_ID)
     from
        "OSTROVA_IMP"."RECORD_ARTICLE"
     where
        ARTICLE_TYPE_ID not in (select old_id from ostrova.article)
     group by
        NAME
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
    NULL,
    sysdate,
    1,                  -- група DELETED
    null,
    0,                  -- IS_ACTIVE 0
    ARTICLE_TYPE_ID
from (
select
    NAME,
    ARTICLE_TYPE_ID
from "OSTROVA_IMP"."RECORD_ARTICLE"
where ARTICLE_TYPE_ID in (
     select
        max(ARTICLE_TYPE_ID)
     from
        "OSTROVA_IMP"."RECORD_ARTICLE"
     where
        ARTICLE_TYPE_ID not in (select old_id from ostrova.article where old_id is not null)
     group by
        NAME
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
    NULL,
    sysdate,
    1,             -- група DELETED
    null,
    0,             -- IS_ACTIVE 0
    ARTICLE_TYPE_ID
from (
select
    NAME,
    ARTICLE_TYPE_ID
from "OSTROVA_IMP"."RECORD_ARTICLE"
where ARTICLE_TYPE_ID in (
     select
       max(ARTICLE_TYPE_ID)
     from
       "OSTROVA_IMP"."RECORD_ARTICLE"
     where
       ARTICLE_TYPE_ID not in (select old_id from ostrova.article where old_id is not null)
     group by
       NAME
) group by name, article_type_id
)
;

-- ############## Импортиране на поръчки
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

-- ############## Импортиране на доставки - детайни записи
-- Артикулите/Артикулите групи се издирват по OLD_ID и се прикачат към новите си идентификатори
-- Артикулите/Артикулите групи, които са били изтрити се издирват само по име
INSERT INTO OSTROVA.ORDER_DETAIL
	select
	OSTROVA.OSTROVACALENDAR_ORDERDETAIL_SQ.NEXTVAL,
    CNT,
	PRICE,
    (select
       ID
     from
       ostrova.article z
     where
           (z.old_id = x.ARTICLE_TYPE_ID and z.name = x.NAME and z.group_fk_id = 1) or
           (z.old_id = x.ARTICLE_TYPE_ID and z.group_fk_id <> 1)
     ) article_id,
	(select
	       GROUP_FK_ID
     from
           ostrova.article z
     where
           (z.old_id = x.ARTICLE_TYPE_ID and z.name = x.NAME and z.group_fk_id = 1) or
           (z.old_id = x.ARTICLE_TYPE_ID and z.group_fk_id <> 1)
    ) article_id,
    REC_ID
	from
 "OSTROVA_IMP"."RECORD_ARTICLE" x
 where rec_id in (select id from OSTROVA."ORDER");

-- Корекция на лиспащ артикул "Детско меню", който не е бил намерен
INSERT INTO OSTROVA.ARTICLE
values(
    OSTROVA.ARTICLE_SQ.nextval,
    'Детско меню',
    NULL,
    NULL,
    0,
    NULL,
    NULL,
    NULL,
    sysdate,
    1,
    null,
    0,
    9998);

-- Ръчна корекция на невалидни записи от старата база
update OSTROVA.ORDER_DETAIL set article_fk_id = (select max(id) from OSTROVA.ARTICLE) , group_fk_id = 1 where article_fk_id is null and order_fk_id in (6148,6205,7815,7856);

commit;

alter Table ostrova.article drop column old_id;




