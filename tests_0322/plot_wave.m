close all
clc
clear

w_con = '2'; % wave case
p_con = 'hd'; % pipe array case

wav1_o = load([w_con,'_',p_con,'_wave1_original.txt']);
wav2_o = load([w_con,'_',p_con,'_wave2_original.txt']);
wav3_o = load([w_con,'_',p_con,'_wave3_original.txt']);
wav1_f = load([w_con,'_',p_con,'_wave1_filtered.txt']);
wav2_f = load([w_con,'_',p_con,'_wave2_filtered.txt']);
wav3_f = load([w_con,'_',p_con,'_wave3_filtered.txt']);


%% plot wave elevation
t = wav1_o(end,1);

figure(1)
subplot(3,1,1)
plot(wav1_o(:,1),wav1_o(:,2),'--k',wav1_o(:,1),wav1_f,'-k')
axis([0 t -inf inf]);
ylabel('\eta (mm)');
xlabel('Time (s)');
legend('raw','filtered')
subplot(3,1,2)
plot(wav2_o(:,1),wav2_o(:,2),'--k',wav2_o(:,1),wav2_f,'-k')
axis([0 t -inf inf]);
ylabel('\eta (mm)');
xlabel('Time (s)');
legend('raw','filtered')
subplot(3,1,3)
plot(wav3_o(:,1),wav3_o(:,2),'--k',wav3_o(:,1),wav3_f,'-k')
axis([0 t -inf inf]);
ylabel('\eta (mm)');
xlabel('Time (s)');
legend('raw','filtered')

%%
dt=wav1_o(2,1)-wav1_o(1,1);
fs=1/dt; % sampling rate
n1 = 10*fs;
n2 = 20*fs;

target = wav1_f(n1:n2);
f1=[];
amp1=[];

NFFT = 2^nextpow2(length(target)); % next power of 2 from length of y
Y = fft(target,NFFT)/length(target);
f1 = fs/2*linspace(0,1,NFFT/2+1);
df = f1(2)-f1(1);
amp1 = 2*abs(Y(1:NFFT/2+1));
[a,k]=max(amp1);
f0=f1(k);

target = wav2_f(n1:n2);
f2=[];
amp2=[];

NFFT = 2^nextpow2(length(target)); % next power of 2 from length of y
Y = fft(target,NFFT)/length(target);
f2 = fs/2*linspace(0,1,NFFT/2+1);
df = f2(2)-f2(1);
amp2 = 2*abs(Y(1:NFFT/2+1));
[a,k]=max(amp2);
f0=f2(k);

target = wav3_f(n1:n2);
f3=[];
amp3=[];

NFFT = 2^nextpow2(length(target)); % next power of 2 from length of y
Y = fft(target,NFFT)/length(target);
f3 = fs/2*linspace(0,1,NFFT/2+1);
df = f3(2)-f3(1);
amp3 = 2*abs(Y(1:NFFT/2+1));
[a,k]=max(amp3);
f0=f3(k);

figure(2)
plot(f1,amp1,f2,amp2,f3,amp3)
ylabel({'Magnitude (cm)'});
xlabel({'Frequency (Hz)'});
legend('gauge 1','gauge 2','gauge 3')
axis([0 5*f0 0 inf]);