create table json_example ( 
id number primary key, 
meadows_json clob, 
constraint meadows_json check (meadows_json is JSON) 
);
