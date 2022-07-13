//调用库
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include "TM1637.h" //提示出错，请按Ctrl+Shift+I 从 库管理器中搜索 TM1637，在结果中选择Grove4-Digit Display并安装

//定义引脚
#define btn D2       //按键引脚
#define level D3     //水位引脚
#define CLK D4       //数码显示管CLK脚
#define DIO D5       //数码显示管DIO脚
#define infrared D6  //红外引脚
#define pump D7      //水泵控制板引脚

TM1637 Tm(CLK, DIO); //定义数码管


// 设置wifi接入信息(请根据您的WiFi信息进行修改，可以是家里wifi，也可以手机共享的wifi热点)
const char* ssid = "baimeiman";       //wifi名称
const char* password = "20020811";    //wifi密码

//定义变量
int Amount  = 5;        //初始水量级别
int MaxAmount  = 12;     //设置最大水量
int FirstSend = true;   //首次水位预警触发标志
int Setwait = 0;
int Waittime = 600;      //消息报送时间间隔，单位秒,600秒，即10分钟
int gt0, gt1, gt2, gt3; //时间数字
bool Showlevel = true;  //首次显示水位级别标志
bool Inittime = true;   //开机初始化时间标志
bool HaveCup = false;   //水杯是否存在标志



void setup() {

  pinMode(level, INPUT);//定义水位引脚
  pinMode(btn, INPUT);//定义按钮引脚
  pinMode(infrared, INPUT);//定义红外引脚
  pinMode(pump, OUTPUT);//定义水泵控制板引脚
  digitalWrite(pump, HIGH);//初始化水泵控制板引脚为高电平，关闭水泵
  //初始化串口设置
  Serial.begin(9600);


  //设置ESP8266工作模式为无线终端模式
  WiFi.mode(WIFI_STA);
  //开始连接wifi
  WiFi.begin(ssid, password);
  //等待WiFi连接,连接成功打印IP
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi 已连接");



  Tm.init();//数码管初始化
  Tm.set(BRIGHT_TYPICAL);//BRIGHT_TYPICAL = 2,BRIGHT_DARKEST = 0,BRIGHTEST = 7;
}

void loop()
{
  if (digitalRead(level) == LOW)   //如果水位低
  {
    //当水位低，即马上发送一次消息，之后每隔一段时间发送一次，Waittime是时间间隔，单位秒。
    if (FirstSend || (SysRunTime() % Waittime == 0 ))
    {
      httpClientRequest();           //发送消息
      FirstSend = false;
      delay(1000);
    }
  }
  else
  {
    FirstSend = true;
  }

  WaterClass(); //调用水位级别调整函数
  ShowTime();   //调用显示时间函数
  PushWater();  //调用水泵控制函数
}


// HTTP发送json数据
void httpClientRequest() {
  // HTTP请求用的URL。注意网址前面必须添加"http://"
  String  URL = "http://wxpusher.zjiecode.com/api/send/message";  //接收json数据接口

  String  tmp1 = "位于1号茶水间的饮用水机,已接近低水位,请尽快加水";
  String  tmp2 = "缺水预警信息";
  String  tmp3 = "6185";  //主题编号(Topics)
  String  APP_TOKEN = "AT_9KIaAiizKtghYJXojFtIOiZgOIzjoY3K";    //用户消息APP_TOKEN：


  //json 数据合成
  String payloadJson = "{\"appToken\":\"";
  payloadJson += APP_TOKEN;
  payloadJson += "\",\"content\":\"";
  payloadJson += tmp1;
  payloadJson += "\",\"summary\":\"";
  payloadJson += tmp2;
  payloadJson += ":";
  payloadJson += tmp1;
  payloadJson += "\",\"contentType\":1,\"topicIds\":[";
  payloadJson += tmp3;
  payloadJson += "],\"uids\":[\"\"],\"url\":\"\"}";


  //创建 HTTPClient 对象
  HTTPClient httpClient;
  //通过begin函数配置请求地址
  httpClient.begin(URL);
  httpClient.addHeader("Content-Type", "application/json");
  int httpCode = httpClient.POST(payloadJson); //向服务器提交json数据，请求捷易快信在微信上推送消息
  if (httpCode == HTTP_CODE_OK) {  //请求成功
    Serial.println("告警已发送");
    Serial.println(httpClient.getString()); //输出返回信息
  }
  else
  {
    Serial.println("告警发送失败");
    Serial.println(httpCode);
  }

  httpClient.end();
  return;
}


//获取网络时间
String gettime()
{
  String GetUrl = "http://quan.suning.com/getSysTime.do"; //时间获取网址
  //创建 httpGettime 对象
  HTTPClient httpGettime;
  //设置访问超时时间
  httpGettime.setTimeout(5000);
  //通过begin函数配置请求地址
  httpGettime.begin(GetUrl);

  int httpCode = httpGettime.GET();
  if (httpCode > 0) {
    Serial.printf("[HTTP] GET... code: %d\n", httpCode);
    if (httpCode == HTTP_CODE_OK) {
      //读取响应内容
      String response = httpGettime.getString();
      // Serial.println(response);
      //得到的字符串格式 {"sysTime2":"2021-04-20 11:53:37","sysTime1":"20210420115337"}

      if   (!(strstr(response.c_str(), "sysTime2") == NULL))//查找sysTime2，如果存在
      {
        return response.substring(13, 23) + " " + response.substring(24, 32); //截取字符串，得到时间格式数据
      }
    }
  }
  else {
    // Serial.printf("[HTTP] GET... failed, error: %s\n", http.errorToString(httpCode).c_str());
  }
  httpGettime.end();
  return "-";
}


//调整出水量
void WaterClass()
{
  do
  {
    //Serial.println(digitalRead(btn));
    if (digitalRead(btn))      //如果调整水量按钮被按下
    {
      Setwait = SysRunTime();
      if  (Showlevel)          //第一次按，显示当前级别,不增加级别
      {
        Showlevel = false;
      }
      else                    //第二次或多次按，调整级别
      {
        Amount ++;
        if (Amount > MaxAmount)       //超过最大水量，即返回1
        {
          Amount = 1;
        }
      }
      ShowValue(Amount);     //显示水量级别
      delay(200);
    }
    delay(3);
  } while (SysRunTime() - Setwait < 3);
  Showlevel = true;
  return;

}


//显示水量级别
void ShowValue(int v)
{
  Tm.point(0);//小数点开关，0为关闭

  //四位数字位置是0,1,2,3，表示第一，第二，第三，第四位
  Tm.clearDisplay();
  if (v > 9)
  {
    Tm.display(2, floor((v - (v % 10)) / 10)); //表示第三位显示
    Tm.display(3, (v % 10)); //表示第四位显示
  }
  else
  {
    Tm.display(3, v); //表示第四位显示
  }
  return;
}



void ShowTime()
{
  String stmp;
  if (((SysRunTime() % 60 == 0)) || Inittime)  //开机Inittime为true，即获取时间，之后就是每60秒获取一次
  {
    String times = gettime();                  //获取时间字符串
    if (!(times == "-"))
    {
      stmp = times.substring(11, 12);          //截取时间字符串
      gt0 = atoi(stmp.c_str());                //转换为整数
      stmp = times.substring(12, 13);
      gt1 = atoi(stmp.c_str());
      stmp = times.substring(14, 15);
      gt2 = atoi(stmp.c_str());
      stmp = times.substring(15, 16);
      gt3 = atoi(stmp.c_str());
      Inittime = false;
      //Serial.println(times);
    }
  }


  if (SysRunTime() % 2 == 0)                   //时间冒号闪烁，2秒显示一次冒号
  {
    Tm.point(1);//小数点开关，1为打开
  } else
  {
    Tm.point(0);//小数点开关，0为关闭
  }

  //显示时间
  Tm.display(0, gt0); //表示第1位显示
  Tm.display(1, gt1); //表示第2位显示
  Tm.display(2, gt2); //表示第3位显示
  Tm.display(3, gt3); //表示第4位显示
  return;
}



//水泵控制
void PushWater()
{
  digitalWrite(pump, HIGH);

  //HaveCup在这里的作用是，当供水完成后，如果杯子没有拿走，HaveCup一直是true，直到杯子拿走，则HaveCup为false
  //用HaveCup来控制杯子要拿走后，在下一次杯子来才会再启动水泵

  if (digitalRead(infrared))  //如果前面没有杯，标志HaveCup设置为false
  {
    HaveCup = false;
  }
  if ((!digitalRead(infrared)) && (!HaveCup))  //如果目前有杯在 并且 在此之前是没有杯子的 (即突然来了杯子)
  {
    digitalWrite(pump, LOW); //开启水泵
    for (int i = 1; i <= Amount + 1; i++)  //根据水位级别Amount循环，出水以及延时
    {
      if (digitalRead(infrared))  //当杯子拿走了
      {
        HaveCup = false;//标志HaveCup设置为true，表示没有杯子
        digitalWrite(pump, HIGH);//关闭水泵
        Inittime = true; //更新时间标志设置为true，水泵停止后，更新时间
        break;  //跳出循环
      }

      if  (i == Amount + 1)     //当达到设定的水量
      {
        HaveCup = true;//标志HaveCup设置为true，表示现在有杯子
        digitalWrite(pump, HIGH);//关闭水泵
        Inittime = true; //更新时间标志设置为true，水泵停止后，更新时间
        break;  //跳出循环
      }

      delay(1000); //控制出水时间，1个级别为持续泵水1秒
    }
  }
  return;
}



//得到系统运行时长，返回时间单位：秒
long SysRunTime()
{
  float ft;
  long lt;
  ft = millis() / 1000; //毫秒转化为秒
  lt = ft; //再转成整数。
  return lt;
}
