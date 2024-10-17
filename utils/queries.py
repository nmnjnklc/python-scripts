queries: dict = {
    "transfer_in_progress_enabled_companies": '''
        SELECT companies.id AS companyId
             , companies.companyName
             , companies.dotNum
        FROM companies
        WHERE transferInProgress = true;
    ''',

    "vehicles_by_company_name": '''
        SELECT vehicles.id
             , vehicles.vehicleId
             , vehicles.vin
             , vehicles.active
        FROM vehicles
        JOIN companies
            ON companies.id = vehicles.companyId
        WHERE companies.companyName = "{0}";
    ''',

    "elds": '''
        SELECT companies.companyName AS 'COMPANY NAME'
             , elds.serialNum AS 'SERIAL NUMBER'
             , elds.status AS 'STATUS'
             , COALESCE(elds.replacementNote, '') AS 'REPLACEMENT NOTE'
             , CASE
                   WHEN elds.forwardUrl = '{0}' THEN 'ELD RIDER'
                   WHEN elds.forwardUrl = '{1}' THEN 'XELD'
                   WHEN elds.forwardUrl = '{2}' THEN 'OPTIMA ELD'
                   WHEN elds.forwardUrl = '{3}' THEN 'PRORIDE ELD'
                   WHEN elds.forwardUrl = '{4}' THEN 'SPARKLE ELD'
                   WHEN elds.forwardUrl = '{5}' THEN 'XPLORE ELD'
                   WHEN elds.forwardUrl = '{6}' THEN 'ROUTEMATE ELD'
                   WHEN elds.forwardUrl = '{7}' THEN 'TX ELD'
                   WHEN elds.forwardUrl = '{8}' THEN 'APEX ELD'
                   WHEN elds.forwardUrl = '{9}' THEN 'PTI ELD'
                   WHEN elds.forwardUrl = '{10}' THEN 'EVA ELD'
                   WHEN elds.forwardUrl = '{11}' THEN 'FORTKNOX ELD'
                   ELSE COALESCE(elds.forwardUrl, '')
               END AS 'FORWARDED TO'
        FROM elds
        LEFT JOIN companies
            ON companies.id = elds.companyId  
        ORDER BY elds.id ASC;
    ''',

    "gps": '''
        SELECT companies.companyName AS 'COMPANY NAME'
             , gps.serialNum AS 'SERIAL NUMBER'
             , gps.status AS 'STATUS'
             , COALESCE(gps.replacementNote, '') AS 'REPLACEMENT NOTE'
        FROM gps
        LEFT JOIN companies
           ON companies.id = gps.companyId
        ORDER BY gps.id ASC;
    ''',

    "cameras": '''
        SELECT companies.companyName AS 'COMPANY NAME' 
             , cameras.serialNum AS 'SERIAL NUMBER'
             , cameras.status AS 'STATUS'
             , COALESCE(cameras.replacementNote, '') AS 'REPLACEMENT NOTE'
        FROM cameras
        LEFT JOIN companies
            ON companies.id = cameras.companyId
        ORDER BY cameras.id ASC;
    ''',

    "tablets": '''
        SELECT companies.companyName AS 'COMPANY NAME'
             , tablets.serialNum AS 'SERIAL NUMBER'
             , tablets.status AS 'STATUS'
             , COALESCE(tablets.replacementNote, '') AS 'REPLACEMENT NOTE'
        FROM tablets
        LEFT JOIN companies
            ON companies.id = tablets.companyId
        ORDER BY tablets.id ASC;
    '''
}
