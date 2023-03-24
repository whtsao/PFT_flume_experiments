close all
clc
clear

% get first frame of the original image
I0=imread(['1 (1).jpg']); % I0 = original image
s = size(I0);
sx = s(2);
sy = s(1);

% show initial frame to get resolution and boundary
% imshow(I0)
imshow(rgb2gray(I0))

% resolution = mm/pixel (this value is calculated in advance)
d1 = 2*2.54/157;
d2 = 2*2.54/173;
d3 = 2*2.54/163;

% picture boundary
tp1 = 300;
bt1 = 700;
lt1 = 4400;
rt1 = 5200;

tp2 = 300;
bt2 = 700;
lt2 = 2400;
rt2 = 3200;

tp3 = 300;
bt3 = 700;
lt3 = 600;
rt3 = 1400;

% 1st gauge location
gx1 = 4843; % = 140"
gb1 = 10; % width of the column gauge for average 

% 2nd gauge location
gx2 = 2915; % = 94"
gb2 = 10; % width of the column gauge for average 

% 3rd gauge location
gx3 = 1027; % = 30"
gb3 = 10; % width of the column gauge for average 

% threshold of RGB
thrR = 120;
thrG = 120;
thrB = 120;

% threshold of gray
gr1 = 100;
gr2 = 100;
gr3 = 90;

% location of the LED (optional)
ledx = 30;
ledy = 30;

% sampling rate
fs = 60;


%% check the animation of the free surface
lite_on = false;

% number of the first and the last pictures
ns = 1880;
nf = 2000;

for n = ns:1:nf
    
I0 = imread(['1 (',num2str(n),').jpg']); % I0 = read original image

% corp and gray
I1_1 = I0(tp1:bt1,lt1:rt1,:); % grab wanted range
% I2_1 = rgb2gray(I1_1); % turn RGB to grey
I2_1 = I1_1; % use RGB to identify image

I1_2 = I0(tp2:bt2,lt2:rt2,:); % grab wanted range
% I2_2 = rgb2gray(I1_2); % turn RGB to grey
I2_2 = I1_2; % use RGB to identify image

I1_3 = I0(tp3:bt3,lt3:rt3,:); % grab wanted range
% I2_3 = rgb2gray(I1_3); % turn RGB to grey
I2_3 = I1_3; % use RGB to identify image

% % find the starting frame of the experiment
% lite_color = I0(ledy,ledx,2); % depend on the LED color
% if(lite_color>240 && lite_on==false)
%     lite_on = true;
%     begin = n; % picture of LED light on (the initial time step of the simulation)
% end

% black or white
nx = size(I2_1,1);
ny = size(I2_1,2);
I3_1 = zeros(nx,ny);
R = I2_1(:,:,1); 
G = I2_1(:,:,2);
B = I2_1(:,:,3);

for i=1:nx
    for j=1:ny
        if (R(i,j)>thrR)&&(G(i,j)<thrG)&&(B(i,j)<thrB)
%         if I2_1(i,j)>gr1
        I3_1(i,j) = 255; % give water white
        else
        I3_1(i,j) = 0; % give air black
        end
    end
end

nx = size(I2_2,1);
ny = size(I2_2,2);
I3_2 = zeros(nx,ny);
R = I2_2(:,:,1); 
G = I2_2(:,:,2);
B = I2_2(:,:,3);

for i=1:nx
    for j=1:ny
        if (R(i,j)>thrR)&&(G(i,j)<thrG)&&(B(i,j)<thrB)
%         if I2_2(i,j)>gr2
        I3_2(i,j) = 255; % give water white
        else
        I3_2(i,j) = 0; % give air black
        end
    end
end

nx = size(I2_3,1);
ny = size(I2_3,2);
I3_3 = zeros(nx,ny);
R = I2_3(:,:,1); 
G = I2_3(:,:,2);
B = I2_3(:,:,3);

for i=1:nx
    for j=1:ny
        if (R(i,j)>thrR)&&(G(i,j)<thrG)&&(B(i,j)<thrB)
%         if I2_3(i,j)>gr3
        I3_3(i,j) = 255; % give water white
        else
        I3_3(i,j) = 0; % give air black
        end
    end
end

% canny
I4_1(:,:,n) = edge(I3_1,'canny'); % acquire edge
I4_2(:,:,n) = edge(I3_2,'canny'); 
I4_3(:,:,n) = edge(I3_3,'canny'); 


% plot if you want to check the comparison
subplot(2,3,3)
% subplot(6,1,1)
imshow(I1_1)
subplot(2,3,6)
% subplot(6,1,2)
imshow(I4_1(:,:,n))

subplot(2,3,2)
% subplot(6,1,3)
imshow(I1_2)
subplot(2,3,5)
% subplot(6,1,4)
imshow(I4_2(:,:,n))

subplot(2,3,1)
% subplot(6,1,5)
imshow(I1_3)
subplot(2,3,4)
% subplot(6,1,6)
imshow(I4_3(:,:,n))

t = round((n-1)/fs,2);
t_string = num2str(t);
sgtitle(['Time=' t_string 's'])
drawnow

% record the logical hostory of the free surface
I5_1(:,:,n)=I4_1(:,gx1-lt1-gb1/2:gx1-lt1+gb1/2,n);
I5_2(:,:,n)=I4_2(:,gx2-lt2-gb2/2:gx2-lt2+gb2/2,n);
I5_3(:,:,n)=I4_3(:,gx3-lt3-gb3/2:gx3-lt3+gb3/2,n);
end

%% compute wave speed

% find crest
i = 1;
for p = ns:nf
    for r = 1:600 %size(I4_1,2)
    for q = 1:size(I4_1,1) %dn-up+1:-1:1
        if I4_2(q,r,p) == 1
            h(r,i) = size(I4_1,1)-q;
            break
        else
            h(r,i) = size(I4_1,1);
        end
    end
    end
    [crest_y(i),crest_x(i)] = max(h(2:end,i));
    i = i+1;
end

% check crest and wave profile
nt = nf-ns;
hx = linspace(1,size(h,1),size(h,1));
for i = 1:nt %nf
plot(crest_x(i),crest_y(i),'or','MarkerFaceColor','r','MarkerSize',10); hold on
plot(hx(3:end),h(3:end,i),'-b')
hold off
% imshow(I4_2(:,:,i))
axis([0 600 0 400]);
% drawnow
t = round((i-1)/fs,2);
t_string = num2str(t);
sgtitle(['Time=' t_string 's'])
pause(0.05)
end

%% compute the wave elevation of the column gauge
nt = nf-ns+1;
t = nt/fs;

% 1st gauge
gw = gb1+1;
h = zeros(gw,1);
wav1 = zeros(nt,2);
for p = 1:nt
    for r = 1:gw
    for q = 1:bt1-tp1+1 %dn-up+1:-1:1
        if I5_1(q,r,p) == 1
            h(r) = q;
            break
        else
            h(r) = 0;
        end
    end
    end
    wav1(p,1) = (p-1)/fs;
    wav1(p,2) = mean(nonzeros(h))*d1;
end

hini = mean(wav1(1:fs,2));
for i = 1:nt
    wav1(i,2) = hini-wav1(i,2);
end

% 2nd gauge
gw = gb2+1;
h = zeros(gw,1);
wav2 = zeros(nt,2);
for p = 1:nt
    for r = 1:gw
    for q = 1:bt2-tp2+1 %dn-up+1:-1:1
        if I5_2(q,r,p) == 1
            h(r) = q;
            break
        else
            h(r) = 0;
        end
    end
    end
    wav2(p,1) = (p-1)/fs;
    wav2(p,2) = mean(nonzeros(h))*d2;
end

hini = mean(wav2(1:fs,2));
for i = 1:nt
    wav2(i,2) = hini-wav2(i,2);
end

% 3rd gauge
gw = gb3+1;
h = zeros(gw,1);
wav3 = zeros(nt,2);
for p = 1:nt
    for r = 1:gw
    for q = 1:bt3-tp3+1 %dn-up+1:-1:1
        if I5_3(q,r,p) == 1
            h(r) = q;
            break
        else
            h(r) = 0;
        end
    end
    end
    wav3(p,1) = (p-1)/fs;
    wav3(p,2) = mean(nonzeros(h))*d3;
end

hini = mean(wav3(1:fs,2));
for i = 1:nt
    wav3(i,2) = hini-wav3(i,2);
end

figure(1)
subplot(3,1,1)
plot(wav1(:,1),wav1(:,2))
axis([0 t -inf inf]);
ylabel('\eta (mm)');
xlabel('Time (s)');
subplot(3,1,2)
plot(wav2(:,1),wav2(:,2))
axis([0 t -inf inf]);
ylabel('\eta (mm)');
xlabel('Time (s)');
subplot(3,1,3)
plot(wav3(:,1),wav3(:,2))
axis([0 t -inf inf]);
ylabel('\eta (mm)');
xlabel('Time (s)');

%% filter

[bf,af]=butter(10,0.5);
new_wav1=filtfilt(bf,af,wav1(:,2));
new_wav2=filtfilt(bf,af,wav2(:,2));
new_wav3=filtfilt(bf,af,wav3(:,2));

figure(2)
subplot(3,1,1)
plot(wav1(:,1),wav1(:,2),'--k',wav1(:,1),new_wav1,'-k')
axis([0 t -inf inf]);
ylabel('\eta (mm)');
xlabel('Time (s)');
legend('raw','filtered')
subplot(3,1,2)
plot(wav2(:,1),wav2(:,2),'--k',wav2(:,1),new_wav2,'-k')
axis([0 t -inf inf]);
ylabel('\eta (mm)');
xlabel('Time (s)');
legend('raw','filtered')
subplot(3,1,3)
plot(wav3(:,1),wav3(:,2),'--k',wav3(:,1),new_wav3,'-k')
axis([0 t -inf inf]);
ylabel('\eta (mm)');
xlabel('Time (s)');
legend('raw','filtered')

%% save animation
for n = ns:60:nf

subplot(1,3,3)
imshow(I4_1(:,:,n))

subplot(1,3,2)
imshow(I4_2(:,:,n))

subplot(1,3,1)
imshow(I4_3(:,:,n))

t = round((n-1)/fs,2);
t_string = num2str(t);
sgtitle(['Time=' t_string 's'])
drawnow

end
