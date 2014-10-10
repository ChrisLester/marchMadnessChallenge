{
TFile *_file0 = TFile::Open("regression_train_tourney.root");
TTree* t = _file0->Get("tourney_results");
TFile* fOut = new TFile("hists.root", "RECREATE");
t->Draw("seed_prob:game_prob>>hAll(20,0,1,20,0,1)");
TH2F* hAll = static_cast<TH2F*> (gDirectory->Get("hAll"));
t->Draw("seed_prob:game_prob>>hWin(20,0,1,20,0,1)","game_outcome==1");
TH2F* hWin = static_cast<TH2F*> (gDirectory->Get("hWin"));
hAll->Sumw2();
hWin->Sumw2();
fOut->cd();
hAll->Write();
hWin->Divide(hAll);
hWin->Write();
fOut->Close();
}
