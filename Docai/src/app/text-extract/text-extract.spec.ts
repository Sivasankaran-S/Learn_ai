import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TextExtract } from './text-extract';

describe('TextExtract', () => {
  let component: TextExtract;
  let fixture: ComponentFixture<TextExtract>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TextExtract]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TextExtract);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
