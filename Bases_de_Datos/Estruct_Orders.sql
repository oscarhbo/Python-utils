-------------------------------
--  MYSQL, POSTGRES
-------------------------------
CREATE TABLE ORDERS (
ORDERID        INT,
ORDERSTATUS    VARCHAR(30),
LASTUPDATED    TIMESTAMP
);

INSERT INTO ORDERS
VALUES (1,'Ordenada', '2023-06-01 12:00:00');

INSERT INTO ORDERS
VALUES (1,'Enviada', '2023-06-09 12:00:25');

INSERT INTO ORDERS
VALUES (2,'Enviada', '2023-07-11 3:05:00');

INSERT INTO ORDERS
VALUES (1,'Enviada', '2023-06-09 11:50:00');

INSERT INTO ORDERS
VALUES (3,'Enviada', '2023-07-12 12:00:00');


INSERT INTO ORDERS
VALUES (4,'Enviada', '2024-05-05 12:34:12');

-------------------------------
--  ORACLE
-------------------------------
CREATE TABLE ORDERS (
ORDERID        NUMBER(14),
ORDERSTATUS    VARCHAR(30),
LASTUPDATED    TIMESTAMP
);

INSERT INTO ORDERS
VALUES (1,'Ordenada', TO_DATE('2023-06-01 12:00:00', 'YYYY-MM-DD HH24:MI:SS'));

INSERT INTO ORDERS
VALUES (1,'Enviada', TO_DATE('2023-06-09 12:00:25', 'YYYY-MM-DD HH24:MI:SS'));

INSERT INTO ORDERS
VALUES (2,'Enviada', TO_DATE('2023-07-11 3:05:00', 'YYYY-MM-DD HH24:MI:SS'));

INSERT INTO ORDERS
VALUES (1,'Enviada', TO_DATE('2023-06-09 11:50:00', 'YYYY-MM-DD HH24:MI:SS'));

INSERT INTO ORDERS
VALUES (3,'Enviada', TO_DATE('2023-07-12 12:00:00', 'YYYY-MM-DD HH24:MI:SS'));