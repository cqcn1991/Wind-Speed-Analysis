%由于原始数据中可能出现格式错误，将其剔除，需要观察格式，确定fdata,a,b
%也可能由于格式错误而报错
%cityid='ABQ';%阿尔布凯克  中部  美国（新墨西哥州）
%cityid='ABR';%阿伯丁 中部  美国（南达科他州）到2013年5月
%cityid='SLE';%塞勒姆  西部  美国（俄勒冈州）
%cityid='LAX';%洛杉矶  西部  美国（加利福尼亚州）
%cityid='DEN';%丹佛  中部  美国（科罗拉多州）
%cityid='HLN';%赫勒纳  中部  美国（蒙大拿州）
%cityid='BIS';%俾斯麦（州府）  中部  美国（北达科他州）
%cityid='TOP';%托皮卡（州府）  中部  美国（堪萨斯州）
cityid='DSM';%得梅因（州府）  中部  美国（衣阿华州）
%cityid='MSP';%明尼阿波利斯  中部  美国（明尼苏达州）
%cityid='SPI';%斯普林菲尔德（州府）  中部  美国（伊利诺斯州）
%cityid='LNK';%林肯（州府）  中部  美国（内布拉斯加州）

%
% city={'HLN'};
% 
% for nn=1:length(city)
    
% cityid=city{nn};

out_dir='D:\风气候分析包\wjc\out\2min_1hour';

if ~isdir([out_dir,'\',cityid])
     mkdir([out_dir,'\',cityid])
end

Vmonth=[];datahourmean=[];
for year=2000:2016
    selectyear=num2str(year);
    if year==2016
        jjj=9;
    else
        jjj=12;
    end       
    
    for jj=1:jjj
        if jj<10
            in_file=['D:\风气候分析包\wjc\1min采样间隔的数据\',selectyear,'\',cityid,selectyear,'0',num2str(jj),'.dat'];
        else
            in_file=['D:\风气候分析包\wjc\1min采样间隔的数据\',selectyear,'\',cityid,selectyear,num2str(jj),'.dat'];
        end      
        
        %读取数据
        fid=fopen(in_file,'r');
%         %fdata=textscan(fid,'%s %s %s %s %s %s %s %s %s %s %s');%cityid='LAX';%洛杉矶  西部  美国（加利福尼亚州）
%         fdata=textscan(fid,'%s %s %s %s %s %s %s %s %s %s');%cityid='ABQ';%阿尔布凯克  中部  美国（新墨西哥州）       
% %         %为了将格式错误的数据剔除，读入c,d,e,f,g,h
%         a=fdata(7);b=fdata(8);c=fdata(9);d=fdata(10);e=fdata(3);f=fdata(4);g=fdata(5);h=fdata(6);
%         data0=[str2double(a{1}) str2double(b{1})];
%         datacd=[str2double(c{1}) str2double(d{1})];
%         dataef=[str2double(e{1}) str2double(f{1})];datagh=[str2double(g{1}) str2double(h{1})];
%         putin=(~isnan(data0(:,1))).*(~isnan(data0(:,2))).*(~isnan(datacd(:,1))).*(~isnan(datacd(:,2))).*(~isnan(dataef(:,1))).*(isnan(dataef(:,2))).*(~isnan(datagh(:,1))).*(isnan(datagh(:,2)));        


        fdata=textscan(fid,'%s %s %s %s %s %s %s %s');%'ABR';%阿伯丁 中部  美国（南达科他州）格式不同
        a=fdata(5);b=fdata(6);c=fdata(7);d=fdata(8);e=fdata(3);f=fdata(4);%'ABR';%阿伯丁 中部  美国（南达科他州）格式不同
        data0=[str2double(a{1}) str2double(b{1})];
        datacd=[str2double(c{1}) str2double(d{1})];
        dataef=[str2double(e{1}) str2double(f{1})];
        putin=(~isnan(data0(:,1))).*(~isnan(data0(:,2))).*(~isnan(datacd(:,1))).*(~isnan(datacd(:,2))).*(~isnan(dataef(:,1))).*(isnan(dataef(:,2)));  

        data=data0(putin~=0,:);
        A=fdata(2);A=A{1};
        A=A(putin~=0,:);
%%%%%%%%%%%%%%%%%%%%%运行，寻找格式错误       
        F=zeros(length(A),1);
        for ii=1:length(A)
            F(ii)=length(A{ii});  
        end
%         find(F~=19)%在A中查找对应行的日期，在原文件中查找错误
%         disp([selectyear,'\',cityid,selectyear,num2str(jj),'.dat'])
%         erro=A(find(F~=19))%找到格式错误的数据
        A(F~=19)=[];
        data(F~=19,:)=[];
%%%%%%%%%%%%%%%%%%%%%
        exempt=find(data(:,1)<0 | data(:,1)>360 | data(:,2)>70 | data(:,2)<0);
        A(exempt)=[];
        data(exempt,:)=[];
        
        %去除突变的数据
        data1=data(:,2);
        J1=[data1(1);diff(data1)];
        J2=[-diff(data1);data1(end)];
        rejectthreshord=20;
        data(J1>rejectthreshord & J2>rejectthreshord,:)=[];
        A(J1>rejectthreshord & J2>rejectthreshord)=[];

        B=cell2mat(A);
        B=B(:,4:13);
                
%         A=fdata(2);A=A{1};B=cell2mat(A);
%         B=B(:,4:13);
        time=str2num(B);
        
        %data=cell2mat([fdata(7) fdata(8)]);
        %data=cell2mat([fdata(5) fdata(6)]);%'ABR';%阿伯丁 中部  美国（南达科他州）格式不同
        disp(['数据共有',num2str(length(A)),'行，检查是否将',selectyear,'\',cityid,selectyear,num2str(jj),'.dat文件中的数据完全读取'])
         fclose(fid);clear A B a b
         
        %转化为矢量
        x=data(:,2).*cos(data(:,1)*pi()/180);
        y=data(:,2).*sin(data(:,1)*pi()/180);
        
        %time1=rem(time,1e4);
        %计算小时平均值
        time1=unique(time);%原始数据可能出现漏测的点
        X1=[];Y1=[];
        for ii=1:length(time1)
            x1=mean(x(time==time1(ii)));
            y1=mean(y(time==time1(ii)));
            X1=[X1;x1];
            Y1=[Y1;y1];
        end
        dir=atan2(Y1,X1)*180/pi();
        dir=(dir+360).*(dir<0)+dir.*(dir>=0);%小时平均风速风向
        
        v=(X1.^2+Y1.^2).^0.5*(1852/3600);%小时平均风速，节转化为m/s
        
        angle=[0:1:15]'*22.5;
        upangle=angle-22.5/2;upangle(1)=upangle(1)+360;
        downangle=angle+22.5/2;
        dir1=dir;
        for ii=2:16
            dir(dir<downangle(ii) & dir>upangle(ii))=ii;
        end
        dir=dir.*(dir1~=dir)+(dir1==dir);%剩下的是1风向角, 小时平均风速风向
        
        %%%%%%%%%%%%%%
        
        V=zeros(1,16);
        for ii=1:16
            if sum(v(dir==ii))
                V(ii)=max(v(dir==ii));
            end
        end
        Vmonth=[Vmonth;V];
        v_and_dir=[time1 v dir];
        datahourmean=[datahourmean;v_and_dir];
    end
end

save([out_dir,'\',cityid,'\Vmonth.mat'],'Vmonth')
save([out_dir,'\',cityid,'\datahourmean.mat'],'datahourmean')

% end