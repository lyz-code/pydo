# FULID

To generate id's that are going to be used in the command line, we are using
a variation of the [ulids](https://github.com/ulid/spec).

## Usage

### Create a brand new FULID.

The timestamp value (48-bits) is from [time.time()](https://docs.python.org/3/library/time.html?highlight=time.time#time.time) with millisecond precision.

The randomness value (45-bits) is from [os.urandom()](https://docs.python.org/3/library/os.html?highlight=os.urandom#os.urandom).

The id value (24-bits) is from a selected character set.

```python
>>> import fulid
>>> fulid().new()
<fulid('01DWF3EZYE0ANTCMCSSAAAAAAA')>
```

### Create the next fulid

```python
>>> import fulid
>>> fulid().new('01DWF3EZYE0ANTCMCSSAAAAAAA')
<fulid('01DWFBFPC4K8MDYBDDBAAAAAAS')>
```


## Specification

Below is the current specification of FULID.

```
 01AN4Z07BY      79KA1307S    AAAAAAA

|----------|    |--------|    |------|
 Timestamp     Randomness        ID
   48bits        9 chars      7 chars
```

### Components

**Timestamp**
- 48 bit integer
- UNIX-time in milliseconds
- Won't run out of space 'til the year 10889 AD.

**Randomness**
- 45 bits
- Cryptographically secure source of randomness, if possible

**ID**
- 24 bits
- Based on a selected character set selected by the user, by default is
  `asdfghjwer` as there are ones that require less finger movement and are not
  forbidden by ulid.
- You can define your own character set, of the length that you want. But they
  should not be part of the forbidden characters, which by default are
  `ilou|&:;()<>~*@?!$#[]{}\\/\'"`.

### Sorting

The left-most character must be sorted first, and the right-most character
sorted last (lexical order). The default ASCII character set must be used.
Within the same millisecond, sort order is not guaranteed.




