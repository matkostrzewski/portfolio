<?php

use Illuminate\Http\Request;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Here is where you can register API routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| is assigned the "api" middleware group. Enjoy building your API!
|
*/

use Illuminate\Support\Facades\DB;

Route::get('/sended/sms/{number}',function($number) {

    $records = DB::select("SELECT `TextDecoded` FROM sentitems WHERE `DestinationNumber` = '$number' OR `DestinationNumber` LIKE '%$number' ORDER BY `ID` DESC LIMIT 1 ");
    return response()->json($records);
});

Route::get('/recived/sms/{number}',function($number) {

    $records = DB::select("SELECT `TextDecoded` FROM inbox WHERE `SenderNumber` = '$number' OR `SenderNumber` LIKE '%$number' ORDER BY `ID` DESC LIMIT 1 ");
    return response()->json($records);
});

Route::post('/send/sms', function(Request $request){
    // POST: number, message args
    $post = $request->post();
    //number 
    $number = $post['number'];
    $numbers = explode(",", $number);
    $message = $post['message'];
    //message
    $creator = "";
    if(isset($post['creator'])){
        $creator = $post['creator'];
    }else{
        $creator = '0';
    }
    //multipart sms
    foreach($numbers as $number){
        if(strlen($message) > 150){
            //multipart msg
            $msgParts = str_split($message,150);
            $text = $msgParts[0];
            $lastID = DB::select("SELECT `ID` , `Status` FROM outbox ORDER BY `ID` DESC LIMIT 1");
            foreach($lastID as $l){
                $lastID = $l->ID;
                break;
            }
            if(!$lastID){
                $lastID = DB::select("SELECT `ID`, `Status` FROM sentitems ORDER BY `ID` DESC LIMIT 1");
                foreach($lastID as $l){
                    $lastID = $l->ID;
                    break;
                }
            }
            $udhBase = "050003";
            $id = "";
            if($lastID){
                $udhHex = $lastID + 1;
                $id = $lastID + 1;
            }else{
                $udhHex = 1;
                $id = 1;
            }
            if(($udhHex % 255) == 0){
                $stack = $udhHex / 255;
                $records = DB::select("SELECT * FROM sentitems WHERE `UDH` NOT LIKE '%_archive_%'");
                foreach($records as $record){
                    $oldUDH = $record->UDH;
                    $updatedUDH = $stack."_archive_".$oldUDH;
                    DB::update("UPDATE sentitems SET `UDH` = '$updatedUDH' WHERE `UDH` = '$oldUDH' ");

                }
            }
            if($udhHex >= 255){
                $udhHex = $udhHex % 255;
            }
            $udhHex = dechex($udhHex);
            $udhHex = str_pad($udhHex, 2, '0', STR_PAD_LEFT);
            $udhMax = count($msgParts);
            $udhMax = str_pad($udhMax, 2, '0', STR_PAD_LEFT);
            $udhPart = $udhBase.$udhHex.$udhMax."01";
            DB::insert("INSERT INTO outbox (`DestinationNumber`,`TextDecoded`,`CreatorID`, `SenderID`, `DeliveryReport`,`MultiPart`,`UDH` ) 
            VALUES ('$number','$text','$creator','', 'default', 'true', '$udhPart')");
            for($i = 1; $i < count($msgParts); $i++){
                $value = $msgParts[$i];
                $msgPart = "";
                $sequence = $i + 1;
                $udhIndex = str_pad($sequence, 2, '0', STR_PAD_LEFT);
                $UdhPart = $udhBase.$udhHex.$udhMax.$udhIndex;
                DB::insert("INSERT INTO outbox_multipart (`TextDecoded`, `UDH`, `ID`, `SequencePosition`) 
                VALUES ('$value' , '$UdhPart', '$id', '$sequence')");
            }
        //one part sms
        }else{
            DB::insert("INSERT INTO outbox (DestinationNumber, TextDecoded , CreatorID) VALUES ('$number' , '$message' , '$creator')");
        }
    }
    $json['sending'] = 'ok';
    return response()->json($json);
});


Route::get('/sended/page/{page}', function($page){
    $page = $page * 25;
    $records = DB::select("SELECT `ID`, `TextDecoded`,`SendingDateTime`, `DestinationNumber`, `UDH`,`CreatorID`, `Status` FROM sentitems ORDER BY `ID` DESC LIMIT 25 OFFSET $page");
    $recs = [];
    foreach($records as $record){
        $udh = substr($record->UDH,-2,2);
        $id = (string) $record->ID;
        if($udh == "" || $udh == "01"){
             if($record->UDH && $udh == "01"){
                $recs[$id] = null;
                $recs[$id]['TextDecoded'] = null;
                 $UDH = substr($record->UDH,0,-4);
                 $multipartRecords = DB::select("SELECT `TextDecoded` FROM sentitems WHERE `UDH` LIKE '$UDH%' ORDER BY `ID` ASC");
                 foreach($multipartRecords as $multipart){
                     $recs[$id]['TextDecoded'] .= $multipart->TextDecoded;
                 }
                 $recs[$id]['SendingDateTime'] = $record->SendingDateTime;
                 $recs[$id]['DestinationNumber'] = $record->DestinationNumber;
                 $recs[$id]['Status'] = $record->Status;
                 $recs[$id]['CreatorID'] = $record->CreatorID;

             }else{
                 $recs[$id] = null;
                 $recs[$id]['TextDecoded'] = null;
                 $recs[$id]['TextDecoded'] = $record->TextDecoded;
                 $recs[$id]['SendingDateTime'] = $record->SendingDateTime;
                 $recs[$id]['DestinationNumber'] = $record->DestinationNumber;
                 $recs[$id]['Status'] = $record->Status;
                 $recs[$id]['CreatorID'] = $record->CreatorID;
             }
        }
    }
             
    return response()->json($recs);
});

Route::get('/recived/page/{page}', function($page){
    $page = $page * 25;
    $records = DB::select("SELECT `ID`, `ReceivingDateTime`,  `TextDecoded`, `SenderNumber`, `UDH`, `readedBy` FROM inbox ORDER BY `ID` DESC LIMIT 25 OFFSET $page");
    $recs = [];
    foreach($records as $record){
        $udh = substr($record->UDH,-2,2);
        $id = (string) $record->ID;
        if($udh == "" || $udh == "01"){
            if($record->UDH && $udh == "01"){
                $recs[$id] = null;
                $recs[$id]['TextDecoded'] = null;
                $UDH = substr($record->UDH,0,-4);
                $multipartRecords = DB::select("SELECT `ID`, `TextDecoded` FROM inbox WHERE `UDH` LIKE '$UDH%' ORDER BY `ID` ASC");
                foreach($multipartRecords as $multipart){
                    $recs[$id]['TextDecoded'] .= $multipart->TextDecoded;
                }
                $recs[$id]['ID'] = $record->ID;
                $recs[$id]['ReceivingDateTime'] = $record->ReceivingDateTime;
                $recs[$id]['SenderNumber'] = $record->SenderNumber;
                $recs[$id]['readed'] = $record->readedBy;
            }else{
                $recs[$id] = null;
                $recs[$id]['ID'] = $record->ID;
                $recs[$id]['TextDecoded'] = null;
                $recs[$id]['TextDecoded'] = $record->TextDecoded;
                $recs[$id]['ReceivingDateTime'] = $record->ReceivingDateTime;
                $recs[$id]['SenderNumber'] = $record->SenderNumber;
                $recs[$id]['readed'] = $record->readedBy;
            }
            $recs[$id]['TextDecoded'] = nl2br($recs[$id]['TextDecoded'] );
        }  
    }
    return response()->json($recs);
});

Route::get('/recived/count', function(){
    $records = DB::select("SELECT COUNT(*) as count FROM inbox");
    return response()->json($records);
});

Route::get('/sended/count', function(){
    $records = DB::select("SELECT COUNT(*) as count FROM sentitems");
    return response()->json($records);
});

Route::get('/phone/signal', function(){
    $records = DB::select("SELECT `Signal` FROM phones");
    return response()->json($records);
});


Route::put('/read/sms/{smsID}/{readerID}', function($smsID, $readerID){
    $id = $smsID;
    $reader = $readerID;
    $records = DB::select("SELECT `readedBy` FROM inbox WHERE `ID` = $id LIMIT 1");
    foreach($records as $record){
        $readers = $record->readedBy.",".$reader;
        DB::update("UPDATE `inbox` SET `readedBy` = '$readers' WHERE `ID` = $id");
    }
    $json['sending'] = 'ok';
    return response()->json($json);
});


