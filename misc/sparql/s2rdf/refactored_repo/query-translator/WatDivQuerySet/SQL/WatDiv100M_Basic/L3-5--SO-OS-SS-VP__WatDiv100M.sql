SELECT tab1.v1 AS v1 , tab0.v0 AS v0 
 FROM    (SELECT sub AS v0 
	 FROM wsdbm__subscribes$$1$$
	 
	 WHERE obj = 'wsdbm:Website12032'
	) tab0
 JOIN    (SELECT obj AS v1 , sub AS v0 
	 FROM wsdbm__likes$$2$$
	) tab1
 ON(tab0.v0=tab1.v0)


++++++Tables Statistic
wsdbm__subscribes$$1$$	1	SS	wsdbm__subscribes/wsdbm__likes
	VP	<wsdbm__subscribes>	1496552
	SS	<wsdbm__subscribes><wsdbm__likes>	355014	0.24
------
wsdbm__likes$$2$$	1	SS	wsdbm__likes/wsdbm__subscribes
	VP	<wsdbm__likes>	1124672
	SS	<wsdbm__likes><wsdbm__subscribes>	222989	0.2
------