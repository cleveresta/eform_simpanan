# BNI eForm Simpanan Service

Repo ini berisi kode program service eForm simpanan yang berbasis Python

# How To Build
Diasumsikan source sudah di-clone ke swarm manager
Image akan di-build di swarm manager
Saat ini, registry yang digunakan adalah registry Harbor (registry internal, perlu login user LDAP atau user outlook apabila belum)

Note: jika update source, pastikan untuk remove dahulu stack nya dengan 

```
docker stack rm <nama stack>
```

untuk tau nama stack

```
docker stack ls 
```
cari eform_simpanan

1. sesuaikan parameter dev dan prod seperti
	- ip, port, user, pass database
	- ip, port endpoint di appconfig.json
	- jika diperlukan, atur alokasi IP (di bagian network) dan/atau exposed port(s) di docker-compose.yml
2. Build image docker dengan command:
```bash
docker-compose build
```
3. Push image docker yang terbentuk dengan command:
```bash
docker-compose push
```
4. Deploy image yang sudah di-push dengan command:
```bash
docker stack deploy --compose-file docker-compose.yml eform_simpanan_web --with-registry-auth
```
	--with-registry-auth dimaksudkan agar autentikasi registry dibawa dari swarm manager tempat image di-push
5. Monitor status deployment dengan command
```bash
docker stack ps eform_simpanan_web
```

# Monitor Log
Log aplikasi dapat dimonitor dengan command berikut di swarm manager:

```bash
docker service logs eform_simpanan_qris-mpm-edc-svc  --follow
```


# Test table
| URL | /eform/simpanan |   |   |
| --- | ----------------|   |   |
| Fields | Length | Type | Mandatory/Optional|
| channel | 60 | String | M |

# Kode error:

| Kode | Message | Keterangan |
| ---- | ------- | ---------- |
| 9001 | TOO MANY OTP REQUEST ATTEMPTS | too many OTP request attempt (not including the first one) |
| 9002 | (SOA) PROSES (status trx), GAGAL INSERT DB | DB Problems |
| 9003 | FAILED TO GENERATE OTP | OTP generation problem |
| 9004 | FAILED TO VALIDATE OTP| OTP validation problem |
| 9005 | INVALID REFERENCE NUMBER | Reference number not valid |
| 9006 | FAILED TO VALIDATE IDENTITY | Photo validation failure |
| 9007 | ERROR WHEN VALIDATE IDENTITY | generic error when validating photo |
| 9008 | ID HAS OPENED ACCOUNT VIA {channel} | the id number has opened an account via channel mentioned |
| 9009 | INVALID INPUT SPECIFIED | there are invalid input in one of fields |
| 9010 | REFERENCE NUMBER CAN NOT BE USED ANYMORE | reference number can not be used again. please start over |
| 9011 | TOO MANY OTP FAILURES | too many otp failures for a reference number |
| 9081 | GENERAL ERROR | general error |