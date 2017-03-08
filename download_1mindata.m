%将程序放在存放下载数据的文件夹
%在美国各城市三字代码及州名中选择城市的代码
%cityid='ABR';%阿伯丁 中部  美国（南达科他州）到2013年5月
%cityid='ABE';%阿伦敦  东部  美国（宾夕法尼亚州）靠近东海岸可能受台风影响
%cityid='ABQ';%阿尔布凯克  中部  美国（新墨西哥州）
%cityid='LAX';%洛杉矶  西部  美国（加利福尼亚州）
%cityid='SEA';%西雅图  西部  美国（华盛顿州）格式太乱
%cityid='SLE';%塞勒姆  西部  美国（俄勒冈州）
%cityid='DEN';%丹佛  中部  美国（科罗拉多州）
%cityid='HLN';%赫勒纳  中部  美国（蒙大拿州）
%cityid='BIS';%俾斯麦（州府）  中部  美国（北达科他州）
%cityid='TOP';%托皮卡（州府）  中部  美国（堪萨斯州）
%cityid='DSM';%得梅因（州府）  中部  美国（衣阿华州）
%cityid='MSP';%明尼阿波利斯  中部  美国（明尼苏达州）
%cityid='SPI';%斯普林菲尔德（州府）  中部  美国（伊利诺斯州）
%cityid='LNK';%林肯（州府）  中部  美国（内布拉斯加州）
cityid='BWI';%巴尔的摩  东部  美国（马里兰州）用来与NOAA的数据对比

disp(cityid)
for year=2001:2015
    selectyear=num2str(year);%选择需要下载的年份
    disp(['下载到',selectyear])
    if ~isdir(selectyear)
        mkdir(selectyear)
    end
    %ftp://ftp.ncdc.noaa.gov/pub/data/asos-onemin/6405-2000/64050KABE200001.dat
    for ii=1:9
        URL=['ftp://ftp.ncdc.noaa.gov/pub/data/asos-onemin/6405-',selectyear,'/64050K',cityid,selectyear,'0',num2str(ii),'.dat'];
        %filename = 'ABE200001.dat';
        filename=[selectyear,'/',cityid,selectyear,'0',num2str(ii),'.dat'];
        outfilename =urlwrite(URL,filename);
    end
    for ii=10:12
        URL=['ftp://ftp.ncdc.noaa.gov/pub/data/asos-onemin/6405-',selectyear,'/64050K',cityid,selectyear,num2str(ii),'.dat'];
        %filename = 'ABE200001.dat';
        filename=[selectyear,'/',cityid,selectyear,num2str(ii),'.dat'];
        outfilename =urlwrite(URL,filename);
    end
end

%2016年只到9月
for year=2016
    selectyear=num2str(year);%选择需要下载的年份
    disp(['下载到',selectyear])
    if ~isdir(selectyear)
        mkdir(selectyear)
    end
    %ftp://ftp.ncdc.noaa.gov/pub/data/asos-onemin/6405-2000/64050KABE200001.dat
    for ii=1:9
        URL=['ftp://ftp.ncdc.noaa.gov/pub/data/asos-onemin/6405-',selectyear,'/64050K',cityid,selectyear,'0',num2str(ii),'.dat'];
        %filename = 'ABE200001.dat';
        filename=[selectyear,'/',cityid,selectyear,'0',num2str(ii),'.dat'];
        outfilename =urlwrite(URL,filename);
    end
end